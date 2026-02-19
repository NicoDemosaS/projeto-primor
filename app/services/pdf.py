from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def gerar_pdf_evento(evento):
    """
    Gera PDF com detalhes de um evento específico
    
    Args:
        evento: Objeto Evento
        
    Returns:
        BytesIO: Buffer com o PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FBBF24'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    
    # Cabeçalho
    elements.append(Paragraph("PRIMOR GARÇONS", title_style))
    elements.append(Paragraph(f"Relatório do Evento", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # Dados do evento
    elements.append(Paragraph(f"<b>Evento:</b> {evento.nome}", normal_style))
    elements.append(Paragraph(f"<b>Tipo:</b> {evento.tipo}", normal_style))
    elements.append(Paragraph(f"<b>Data:</b> {evento.data_formatada}", normal_style))
    elements.append(Paragraph(f"<b>Horário:</b> {evento.horario}", normal_style))
    elements.append(Paragraph(f"<b>Local:</b> {evento.local}", normal_style))
    elements.append(Paragraph(f"<b>Status:</b> {evento.status.capitalize()}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Tabela de garçons
    elements.append(Paragraph("Escala de Garçons", subtitle_style))
    
    # Dados da tabela
    data = [['Nome', 'Função', 'Valor', 'Status']]
    
    for escala in evento.escalas.all():
        status_texto = escala.status.capitalize()
        # Definir função (Garçom ou Garçom/Motorista)
        funcao = 'Garçom/Motorista' if escala.is_motorista else 'Garçom'
        # Calcular valor total (base + adicional motorista se aplicável)
        valor_total = float(escala.valor) + (float(evento.valor_motorista or 0) if escala.is_motorista else 0)
        data.append([
            escala.garcom.nome,
            funcao,
            f'R$ {valor_total:,.2f}',
            status_texto
        ])
    
    # Criar tabela
    table = Table(data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Corpo
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Resumo
    elements.append(Paragraph("Resumo", subtitle_style))
    elements.append(Paragraph(f"<b>Total de garçons:</b> {evento.total_garcons}", normal_style))
    elements.append(Paragraph(f"<b>Confirmados:</b> {evento.total_confirmados}", normal_style))
    elements.append(Paragraph(f"<b>Pendentes:</b> {evento.total_pendentes}", normal_style))
    elements.append(Paragraph(f"<b>Recusados:</b> {evento.total_recusados}", normal_style))
    elements.append(Paragraph(f"<b>Valor total:</b> R$ {evento.valor_total:,.2f}", normal_style))
    
    # Rodapé
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    elements.append(Paragraph("Primor Garçons - Sistema de Gestão de Escalas", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def gerar_pdf_relatorio_geral(eventos, data_inicio=None, data_fim=None):
    """
    Gera PDF com relatório geral de vários eventos
    
    Args:
        eventos: Lista de eventos
        data_inicio: Data inicial do período
        data_fim: Data final do período
        
    Returns:
        BytesIO: Buffer com o PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FBBF24'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    
    # Cabeçalho
    elements.append(Paragraph("PRIMOR GARÇONS", title_style))
    elements.append(Paragraph("Relatório Geral de Eventos", subtitle_style))
    
    # Período
    if data_inicio and data_fim:
        elements.append(Paragraph(
            f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", 
            normal_style
        ))
    
    elements.append(Spacer(1, 20))
    
    # Tabela de eventos
    data = [['Data', 'Evento', 'Local', 'Garçons', 'Valor Total']]
    
    valor_total_geral = 0
    total_garcons = 0
    
    for evento in eventos:
        valor = evento.valor_total
        valor_total_geral += valor
        total_garcons += evento.total_garcons
        
        data.append([
            evento.data_formatada,
            evento.nome[:30],
            evento.local[:25],
            str(evento.total_garcons),
            f'R$ {valor:,.2f}'
        ])
    
    # Criar tabela
    table = Table(data, colWidths=[2.5*cm, 5*cm, 4*cm, 2*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Resumo geral
    elements.append(Paragraph("Resumo Geral", subtitle_style))
    elements.append(Paragraph(f"<b>Total de eventos:</b> {len(eventos)}", normal_style))
    elements.append(Paragraph(f"<b>Total de garçons escalados:</b> {total_garcons}", normal_style))
    elements.append(Paragraph(f"<b>Valor total:</b> R$ {valor_total_geral:,.2f}", normal_style))
    
    # Rodapé
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    elements.append(Paragraph("Primor Garçons - Sistema de Gestão de Escalas", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def gerar_pdf_garcons(garcons):
    """
    Gera PDF com lista de garçons
    
    Args:
        garcons: Lista de garçons
        
    Returns:
        BytesIO: Buffer com o PDF gerado
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FBBF24'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    
    # Cabeçalho
    elements.append(Paragraph("PRIMOR GARÇONS", title_style))
    elements.append(Paragraph("Lista de Garçons Ativos", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # Tabela de garçons
    data = [['Nome', 'Telefone', 'E-mail', 'Idade', 'Eventos']]
    
    for garcom in garcons:
        data.append([
            garcom.nome,
            garcom.telefone,
            garcom.email,
            str(garcom.idade),
            str(garcom.total_eventos)
        ])
    
    # Criar tabela
    table = Table(data, colWidths=[5*cm, 3*cm, 5*cm, 1.5*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (3, 1), (4, -1), 'CENTER'),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Resumo
    elements.append(Paragraph(f"<b>Total de garçons ativos:</b> {len(garcons)}", normal_style))
    
    # Rodapé
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    elements.append(Paragraph("Primor Garçons - Sistema de Gestão de Escalas", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def gerar_pdf_eventos_mes(eventos, mes, ano):
    """
    Gera PDF com eventos do mês
    
    Args:
        eventos: Lista de eventos
        mes: Número do mês
        ano: Ano
        
    Returns:
        BytesIO: Buffer com o PDF gerado
    """
    meses = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#FBBF24'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    
    # Cabeçalho
    elements.append(Paragraph("PRIMOR GARÇONS", title_style))
    elements.append(Paragraph(f"Eventos de {meses[mes]} de {ano}", subtitle_style))
    elements.append(Spacer(1, 20))
    
    if not eventos:
        elements.append(Paragraph("Nenhum evento programado para este mês.", normal_style))
    else:
        # Tabela de eventos
        data = [['Data', 'Horário', 'Evento', 'Local', 'Garçons']]
        
        for evento in eventos:
            data.append([
                evento.data.strftime('%d/%m'),
                evento.horario,
                evento.nome[:25],
                evento.local[:20],
                str(evento.total_garcons)
            ])
        
        # Criar tabela
        table = Table(data, colWidths=[2*cm, 2.5*cm, 5*cm, 4.5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
            
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Resumo
        total_garcons = sum(e.total_garcons for e in eventos)
        valor_total = sum(e.valor_total for e in eventos)
        
        elements.append(Paragraph(f"<b>Total de eventos:</b> {len(eventos)}", normal_style))
        elements.append(Paragraph(f"<b>Total de garçons escalados:</b> {total_garcons}", normal_style))
        elements.append(Paragraph(f"<b>Valor total estimado:</b> R$ {valor_total:,.2f}", normal_style))
    
    # Rodapé
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9CA3AF'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    elements.append(Paragraph("Primor Garçons - Sistema de Gestão de Escalas", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return buffer