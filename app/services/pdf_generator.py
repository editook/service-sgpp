from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def draw_pdf_report(data_rows, title, report_type="Institucional"):
    """
    Función utilitaria para generar un PDF en memoria (BytesIO) usando ReportLab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Encabezado
    elements.append(Paragraph(f"<b>SGPP - Sistema de Gestión Pericial Psicológica</b>", styles['Heading1']))
    elements.append(Paragraph(f"Reporte {report_type}: {title}", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Tabla
    if data_rows:
        table_data = [list(data_rows[0].keys())] # Headers
        for row in data_rows:
            table_data.append([str(v) for v in row.values()])
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#7c3aed")), # Tailwind primary-600
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f5f3ff")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#e5e7eb")),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("<i>No hay datos disponibles para este periodo.</i>", styles['Normal']))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
