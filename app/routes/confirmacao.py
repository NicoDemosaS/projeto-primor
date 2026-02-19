from flask import Blueprint, render_template, request, current_app
from datetime import datetime

from app import db
from app.models import Escala, Garcom

confirmacao_bp = Blueprint('confirmacao', __name__, url_prefix='/confirmar')


@confirmacao_bp.route('/escala-<int:evento_id>-<int:garcom_id>', methods=['GET'])
def confirmar_por_garcom(evento_id, garcom_id):
    """Confirma a escala pendente para um garcom em um evento."""
    now = datetime.now()

    garcom = Garcom.query.get(garcom_id)
    if not garcom:
        return render_template('confirmacao/invalido.html', now=now), 404

    escala = Escala.query.filter_by(
        garcom_id=garcom.id,
        evento_id=evento_id,
    ).order_by(Escala.created_at.desc()).first()

    if not escala:
        return render_template('confirmacao/invalido.html', now=now), 404

    if escala.status != 'pendente':
        return render_template('confirmacao/ja_respondido.html', escala=escala, now=now)

    escala.status = 'confirmado'
    escala.respondido_em = datetime.now()
    db.session.commit()

    return render_template(
        'confirmacao/presenca_confirmada.html',
        garcom=garcom,
        escala=escala,
        evento=escala.evento,
        now=now,
    )


@confirmacao_bp.route('/<token>', methods=['GET', 'POST'])
def confirmar(token):
    """Página pública para confirmação do garçom"""
    escala = Escala.query.filter_by(token=token).first()
    now = datetime.now()
    
    if not escala:
        return render_template('confirmacao/invalido.html', now=now), 404
    
    # Verificar se já respondeu
    if escala.status != 'pendente':
        return render_template('confirmacao/ja_respondido.html', escala=escala, now=now)
    
    if request.method == 'POST':
        resposta = request.form.get('resposta')
        
        if resposta == 'confirmado':
            escala.status = 'confirmado'
        else:
            escala.status = 'recusado'
        
        escala.respondido_em = datetime.now()
        db.session.commit()
        
        return render_template('confirmacao/sucesso.html', 
            escala=escala, 
            evento=escala.evento,
            confirmado=(resposta == 'confirmado'),
            now=now
        )
    
    return render_template('confirmacao/confirmar.html', 
        escala=escala, 
        evento=escala.evento, 
        garcom=escala.garcom,
        now=now
    )
