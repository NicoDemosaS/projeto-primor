from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from datetime import datetime, time
from sqlalchemy import func, case

from app import db
from app.models import Evento, Garcom, Escala
from app.services.whatsapp import enviar_notificacao_whatsapp

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

_END_OF_DAY = time(23, 59, 59)


def _effective_end(hora_inicio, hora_fim):
    """Retorna hora_fim efetiva para comparação de sobreposição.
    
    Se hora_fim é None, falsy (00:00) ou <= hora_inicio (cruza meia-noite),
    trata como fim do dia (23:59:59).
    """
    if not hora_fim or hora_fim <= hora_inicio:
        return _END_OF_DAY
    return hora_fim


def _sql_effective_end():
    """Expressão SQL equivalente a _effective_end para a coluna Evento."""
    return case(
        (Evento.hora_fim.is_(None), _END_OF_DAY),
        (Evento.hora_fim <= Evento.hora_inicio, _END_OF_DAY),
        else_=Evento.hora_fim,
    )


def _garcom_tem_conflito(garcom_id, evento):
    """Verifica conflito de horario do garcom em outro evento no mesmo dia."""
    current_start = evento.hora_inicio
    current_end = _effective_end(evento.hora_inicio, evento.hora_fim)
    other_end = _sql_effective_end()

    conflito = (
        db.session.query(Escala.id)
        .join(Evento, Escala.evento_id == Evento.id)
        .filter(
            Escala.garcom_id == garcom_id,
            Evento.data == evento.data,
            Evento.id != evento.id,
            Evento.hora_inicio < current_end,
            other_end > current_start,
        )
        .first()
    )

    return conflito is not None


def _listar_conflitos(garcom_ids, evento):
    """Retorna conflitos por garcom para exibir no modal de selecao."""
    if not garcom_ids:
        return {}

    current_start = evento.hora_inicio
    current_end = _effective_end(evento.hora_inicio, evento.hora_fim)
    other_end = _sql_effective_end()

    rows = (
        db.session.query(Escala.garcom_id, Evento.nome, Evento.hora_inicio, Evento.hora_fim)
        .join(Evento, Escala.evento_id == Evento.id)
        .filter(
            Escala.garcom_id.in_(garcom_ids),
            Evento.data == evento.data,
            Evento.id != evento.id,
            Evento.hora_inicio < current_end,
            other_end > current_start,
        )
        .all()
    )

    conflitos = {}
    for garcom_id, nome, hora_inicio, hora_fim in rows:
        periodo = hora_inicio.strftime('%H:%M')
        if hora_fim:
            periodo = f"{periodo} - {hora_fim.strftime('%H:%M')}"
        label = f"{nome} ({periodo})"
        conflitos.setdefault(garcom_id, []).append(label)

    return conflitos


@eventos_bp.route('/')
@login_required
def index():
    """Lista de eventos"""
    filtro = request.args.get('filtro', 'todos')
    busca = request.args.get('busca', '').strip()
    
    query = Evento.query
    
    # Filtro por status
    if filtro == 'planejado':
        query = query.filter_by(status='planejado')
    elif filtro == 'notificado':
        query = query.filter_by(status='notificado')
    elif filtro == 'realizado':
        query = query.filter_by(status='realizado')
    elif filtro == 'proximos':
        query = query.filter(Evento.data >= datetime.now().date())
    
    # Busca por nome
    if busca:
        query = query.filter(Evento.nome.ilike(f'%{busca}%'))
    
    eventos = query.order_by(Evento.data.desc()).all()
    
    return render_template('eventos/index.html', 
        eventos=eventos, 
        filtro=filtro,
        busca=busca
    )


@eventos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Criar novo evento"""
    garcons = Garcom.query.filter_by(ativo=True).order_by(Garcom.nome).all()
    
    if request.method == 'POST':
        try:
            # Obter valores
            valor_padrao = request.form.get('valor_padrao', '0')
            valor_padrao = float(valor_padrao.replace(',', '.')) if valor_padrao else 0
            valor_motorista = request.form.get('valor_motorista', '0')
            valor_motorista = float(valor_motorista.replace(',', '.')) if valor_motorista else 0
            
            # Criar evento
            evento = Evento(
                nome=request.form.get('nome', '').strip(),
                tipo=request.form.get('tipo', '').strip(),
                data=datetime.strptime(request.form.get('data'), '%d/%m/%Y').date(),
                hora_inicio=datetime.strptime(request.form.get('hora_inicio'), '%H:%M').time(),
                hora_fim=datetime.strptime(request.form.get('hora_fim'), '%H:%M').time() if request.form.get('hora_fim') else None,
                local=request.form.get('local', '').strip(),
                descricao=request.form.get('descricao', '').strip() or None,
                valor_padrao=valor_padrao,
                valor_motorista=valor_motorista,
                status='planejado'
            )
            
            db.session.add(evento)
            db.session.flush()  # Para obter o ID do evento
            
            # Adicionar garçons à escala com valor padrão do evento
            garcons_ids = request.form.getlist('garcons')
            for garcom_id in garcons_ids:
                escala = Escala(
                    evento_id=evento.id,
                    garcom_id=int(garcom_id),
                    valor=valor_padrao,  # Usa valor padrão do evento
                    is_motorista=False,
                    status='pendente'
                )
                db.session.add(escala)
            
            db.session.commit()
            
            flash(f'Evento "{evento.nome}" criado com sucesso!', 'success')
            return redirect(url_for('eventos.detalhe', id=evento.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar evento: {str(e)}', 'error')
    
    return render_template('eventos/form.html', evento=None, garcons=garcons)


@eventos_bp.route('/<int:id>')
@login_required
def detalhe(id):
    """Detalhe do evento"""
    evento = Evento.query.get_or_404(id)
    garcons_disponiveis = Garcom.query.filter_by(ativo=True).order_by(Garcom.nome).all()
    
    # Remover garçons já escalados
    garcons_escalados_ids = [e.garcom_id for e in evento.escalas.all()]
    garcons_disponiveis = [g for g in garcons_disponiveis if g.id not in garcons_escalados_ids]
    
    conflitos = _listar_conflitos([g.id for g in garcons_disponiveis], evento)

    return render_template('eventos/detalhe.html', 
        evento=evento,
        garcons_disponiveis=garcons_disponiveis,
        conflitos=conflitos
    )


@eventos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar evento"""
    evento = Evento.query.get_or_404(id)
    garcons = Garcom.query.filter_by(ativo=True).order_by(Garcom.nome).all()
    
    if request.method == 'POST':
        try:
            # Obter valores
            valor_padrao = request.form.get('valor_padrao', '0')
            valor_padrao = float(valor_padrao.replace(',', '.')) if valor_padrao else 0
            valor_motorista = request.form.get('valor_motorista', '0')
            valor_motorista = float(valor_motorista.replace(',', '.')) if valor_motorista else 0
            
            evento.nome = request.form.get('nome', '').strip()
            evento.tipo = request.form.get('tipo', '').strip()
            evento.data = datetime.strptime(request.form.get('data'), '%d/%m/%Y').date()
            evento.hora_inicio = datetime.strptime(request.form.get('hora_inicio'), '%H:%M').time()
            evento.hora_fim = datetime.strptime(request.form.get('hora_fim'), '%H:%M').time() if request.form.get('hora_fim') else None
            evento.local = request.form.get('local', '').strip()
            evento.descricao = request.form.get('descricao', '').strip() or None
            evento.valor_padrao = valor_padrao
            evento.valor_motorista = valor_motorista
            
            db.session.commit()
            
            if evento.status == 'notificado':
                flash('⚠️ Atenção: Este evento já foi notificado. Os garçons não receberão as alterações automaticamente.', 'warning')
            
            flash(f'Evento "{evento.nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('eventos.detalhe', id=evento.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar evento: {str(e)}', 'error')
    
    return render_template('eventos/form.html', evento=evento, garcons=garcons)


@eventos_bp.route('/<int:id>/adicionar-garcom', methods=['POST'])
@login_required
def adicionar_garcom(id):
    """Adicionar garçons à escala"""
    evento = Evento.query.get_or_404(id)
    
    try:
        garcons_ids = request.form.getlist('garcons')
        if not garcons_ids:
            flash('Nenhum garçom selecionado.', 'warning')
            return redirect(url_for('eventos.detalhe', id=id))
        
        adicionados = 0
        conflitos = 0
        for garcom_id in garcons_ids:
            garcom_id = int(garcom_id)
            
            # Verificar se já está escalado
            existente = Escala.query.filter_by(evento_id=id, garcom_id=garcom_id).first()
            if existente:
                continue

            if _garcom_tem_conflito(garcom_id, evento):
                conflitos += 1
                continue
            
            escala = Escala(
                evento_id=id,
                garcom_id=garcom_id,
                valor=float(evento.valor_padrao or 0),  # Usa valor padrão do evento
                is_motorista=False,
                status='pendente'
            )
            db.session.add(escala)
            adicionados += 1
        
        db.session.commit()
        
        if adicionados > 0:
            flash(f'{adicionados} garçom(s) adicionado(s) à escala!', 'success')
        if conflitos > 0:
            flash(f'{conflitos} garçom(s) com conflito de horário não foram adicionados.', 'warning')
        if adicionados == 0 and conflitos == 0:
            flash('Os garçons selecionados já estavam escalados.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar garçom: {str(e)}', 'error')
    
    return redirect(url_for('eventos.detalhe', id=id))


@eventos_bp.route('/<int:id>/remover-garcom/<int:garcom_id>', methods=['POST'])
@login_required
def remover_garcom(id, garcom_id):
    """Remover garçom da escala"""
    escala = Escala.query.filter_by(evento_id=id, garcom_id=garcom_id).first_or_404()
    
    try:
        nome = escala.garcom.nome
        db.session.delete(escala)
        db.session.commit()
        
        flash(f'Garçom {nome} removido da escala!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover garçom: {str(e)}', 'error')
    
    return redirect(url_for('eventos.detalhe', id=id))


@eventos_bp.route('/<int:id>/atualizar-escala/<int:escala_id>', methods=['POST'])
@login_required
def atualizar_escala(id, escala_id):
    """Atualizar valor e status de motorista de uma escala"""
    escala = Escala.query.get_or_404(escala_id)
    
    if escala.evento_id != id:
        flash('Escala não pertence a este evento.', 'error')
        return redirect(url_for('eventos.detalhe', id=id))
    
    try:
        # Atualizar valor
        valor = request.form.get('valor', '0')
        escala.valor = float(valor.replace(',', '.')) if valor else 0
        
        # Atualizar motorista
        escala.is_motorista = request.form.get('is_motorista') == 'on'
        
        db.session.commit()
        flash(f'Escala de {escala.garcom.nome} atualizada!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar escala: {str(e)}', 'error')
    
    return redirect(url_for('eventos.detalhe', id=id))


@eventos_bp.route('/<int:id>/notificar', methods=['POST'])
@login_required
def notificar(id):
    """Enviar notificações para todos os garçons do evento"""
    evento = Evento.query.get_or_404(id)
    
    if evento.escalas.count() == 0:
        flash('Não há garçons escalados para este evento.', 'warning')
        return redirect(url_for('eventos.detalhe', id=id))
    
    sucessos = 0
    erros = 0
    
    for escala in evento.escalas.all():
        try:
            # Regenerar token
            escala.regenerar_token()
            
            # Enviar WhatsApp
            resultado = enviar_notificacao_whatsapp(escala)
            
            if resultado:
                escala.notificado_em = datetime.now()
                sucessos += 1
            else:
                erros += 1
                
        except Exception as e:
            erros += 1
            print(f'Erro ao notificar {escala.garcom.nome}: {e}')
    
    # Atualizar status do evento
    evento.status = 'notificado'
    db.session.commit()
    
    if erros == 0:
        flash(f'✅ Notificações enviadas para {sucessos} garçons!', 'success')
    else:
        flash(f'⚠️ {sucessos} enviadas, {erros} falharam.', 'warning')
    
    return redirect(url_for('eventos.detalhe', id=id))


@eventos_bp.route('/<int:id>/notificar-garcom/<int:escala_id>', methods=['POST'])
@login_required
def notificar_garcom(id, escala_id):
    """Reenviar notificação para um garçom específico"""
    escala = Escala.query.get_or_404(escala_id)
    
    try:
        escala.regenerar_token()
        resultado = enviar_notificacao_whatsapp(escala)
        
        if resultado:
            escala.notificado_em = datetime.now()
            db.session.commit()
            flash(f'Notificação reenviada para {escala.garcom.nome}!', 'success')
        else:
            flash(f'Erro ao enviar notificação para {escala.garcom.nome}.', 'error')
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('eventos.detalhe', id=id))


@eventos_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir evento"""
    evento = Evento.query.get_or_404(id)
    
    try:
        nome = evento.nome
        db.session.delete(evento)
        db.session.commit()
        
        flash(f'Evento "{nome}" excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir evento: {str(e)}', 'error')
    
    return redirect(url_for('eventos.index'))


@eventos_bp.route('/<int:id>/marcar-realizado', methods=['POST'])
@login_required
def marcar_realizado(id):
    """Marcar evento como realizado"""
    evento = Evento.query.get_or_404(id)
    
    try:
        evento.status = 'realizado'
        db.session.commit()
        flash(f'Evento "{evento.nome}" marcado como realizado!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('eventos.detalhe', id=id))
