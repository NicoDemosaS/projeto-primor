from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime, timedelta
from sqlalchemy import and_

from app.models import Evento, Escala

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    hoje = datetime.now().date()
    
    # Próximos eventos (próximos 30 dias)
    proximos_eventos = Evento.query.filter(
        Evento.data >= hoje,
        Evento.data <= hoje + timedelta(days=30)
    ).order_by(Evento.data.asc()).limit(5).all()
    
    # Eventos de hoje
    eventos_hoje = Evento.query.filter(Evento.data == hoje).all()
    
    # Confirmações pendentes
    pendentes = Escala.query.filter_by(status='pendente').join(Evento).filter(
        Evento.data >= hoje
    ).count()
    
    # Estatísticas gerais
    total_eventos_mes = Evento.query.filter(
        Evento.data >= hoje.replace(day=1)
    ).count()
    
    total_confirmados = Escala.query.filter_by(status='confirmado').join(Evento).filter(
        Evento.data >= hoje
    ).count()
    
    return render_template('dashboard/index.html',
        proximos_eventos=proximos_eventos,
        eventos_hoje=eventos_hoje,
        pendentes=pendentes,
        total_eventos_mes=total_eventos_mes,
        total_confirmados=total_confirmados
    )
