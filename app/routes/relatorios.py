from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from datetime import datetime, date
from calendar import monthrange
from io import BytesIO

from app.models import Evento, Escala, Garcom
from app.services.pdf import gerar_pdf_evento, gerar_pdf_relatorio_geral, gerar_pdf_garcons, gerar_pdf_eventos_mes

relatorios_bp = Blueprint('relatorios', __name__, url_prefix='/relatorios')


@relatorios_bp.route('/')
@login_required
def index():
    """Página principal de relatórios"""
    eventos = Evento.query.order_by(Evento.data.desc()).limit(20).all()
    return render_template('relatorios/index.html', eventos=eventos)


@relatorios_bp.route('/evento/<int:id>/pdf')
@login_required
def evento_pdf(id):
    """Gerar PDF de um evento específico"""
    evento = Evento.query.get_or_404(id)
    
    pdf_buffer = gerar_pdf_evento(evento)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=evento_{evento.id}_{evento.data}.pdf'
    
    return response


@relatorios_bp.route('/garcons/pdf')
@login_required
def garcons_pdf():
    """Gerar PDF com lista de garçons"""
    garcons = Garcom.query.filter_by(ativo=True).order_by(Garcom.nome).all()
    
    pdf_buffer = gerar_pdf_garcons(garcons)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=garcons.pdf'
    
    return response


@relatorios_bp.route('/eventos-mes/pdf')
@login_required
def eventos_mes_pdf():
    """Gerar PDF com eventos do mês atual"""
    hoje = date.today()
    primeiro_dia = date(hoje.year, hoje.month, 1)
    ultimo_dia = date(hoje.year, hoje.month, monthrange(hoje.year, hoje.month)[1])
    
    eventos = Evento.query.filter(
        Evento.data >= primeiro_dia,
        Evento.data <= ultimo_dia
    ).order_by(Evento.data).all()
    
    pdf_buffer = gerar_pdf_eventos_mes(eventos, hoje.month, hoje.year)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=eventos_{hoje.month}_{hoje.year}.pdf'
    
    return response


@relatorios_bp.route('/geral/pdf')
@login_required
def geral_pdf():
    """Gerar PDF de relatório geral por período"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Evento.query
    
    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Evento.data >= data_inicio)
    
    if data_fim:
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Evento.data <= data_fim)
    
    eventos = query.order_by(Evento.data.desc()).all()
    
    pdf_buffer = gerar_pdf_relatorio_geral(eventos, data_inicio, data_fim)
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=relatorio_geral.pdf'
    
    return response
