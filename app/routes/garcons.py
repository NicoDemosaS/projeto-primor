from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from app import db
from app.models import Garcom

garcons_bp = Blueprint('garcons', __name__, url_prefix='/garcons')


@garcons_bp.route('/')
@login_required
def index():
    """Lista de garçons"""
    filtro = request.args.get('filtro', 'ativos')
    busca = request.args.get('busca', '').strip()
    
    query = Garcom.query
    
    # Filtro por status
    if filtro == 'ativos':
        query = query.filter_by(ativo=True)
    elif filtro == 'inativos':
        query = query.filter_by(ativo=False)
    
    # Busca por nome
    if busca:
        query = query.filter(Garcom.nome.ilike(f'%{busca}%'))
    
    garcons = query.order_by(Garcom.nome.asc()).all()
    
    return render_template('garcons/index.html', 
        garcons=garcons, 
        filtro=filtro,
        busca=busca
    )


@garcons_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cadastrar novo garçom"""
    if request.method == 'POST':
        try:
            garcom = Garcom(
                nome=request.form.get('nome', '').strip(),
                email=request.form.get('email', '').strip(),
                telefone=request.form.get('telefone', '').strip(),
                idade=int(request.form.get('idade', 0)),
                descricao=request.form.get('descricao', '').strip() or None,
                pix=request.form.get('pix', '').strip() or None,
                ativo=True
            )
            
            db.session.add(garcom)
            db.session.commit()
            
            flash(f'Garçom {garcom.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('garcons.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar garçom: {str(e)}', 'error')
    
    return render_template('garcons/form.html', garcom=None)


@garcons_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar garçom"""
    garcom = Garcom.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            garcom.nome = request.form.get('nome', '').strip()
            garcom.email = request.form.get('email', '').strip()
            garcom.telefone = request.form.get('telefone', '').strip()
            garcom.idade = int(request.form.get('idade', 0))
            garcom.descricao = request.form.get('descricao', '').strip() or None
            garcom.pix = request.form.get('pix', '').strip() or None
            
            db.session.commit()
            
            flash(f'Garçom {garcom.nome} atualizado com sucesso!', 'success')
            return redirect(url_for('garcons.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar garçom: {str(e)}', 'error')
    
    return render_template('garcons/form.html', garcom=garcom)


@garcons_bp.route('/<int:id>/toggle-ativo', methods=['POST'])
@login_required
def toggle_ativo(id):
    """Ativar/inativar garçom"""
    garcom = Garcom.query.get_or_404(id)
    
    try:
        garcom.ativo = not garcom.ativo
        db.session.commit()
        
        status = 'ativado' if garcom.ativo else 'inativado'
        flash(f'Garçom {garcom.nome} {status} com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar status: {str(e)}', 'error')
    
    return redirect(url_for('garcons.index'))


@garcons_bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    """Excluir garçom"""
    garcom = Garcom.query.get_or_404(id)
    
    try:
        nome = garcom.nome
        db.session.delete(garcom)
        db.session.commit()
        
        flash(f'Garçom {nome} excluído com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir garçom: {str(e)}', 'error')
    
    return redirect(url_for('garcons.index'))
