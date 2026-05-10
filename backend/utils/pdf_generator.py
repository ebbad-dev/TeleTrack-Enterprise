"""
TeleTrack Enterprise — PDF Generation Utility
Generates formatted PDF reports from tabular data.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_report(title, data):
    """
    Generate a PDF report from a list of dictionaries.
    Returns the binary PDF content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter),
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Title Style
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00f0ff'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=1
    )

    elements.append(Paragraph(f"TeleTrack Enterprise: {title}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    
    if not data:
        elements.append(Paragraph("No data available for this report.", styles['Normal']))
        doc.build(elements)
        return buffer.getvalue()

    # Extract headers and format data
    headers = list(data[0].keys())
    # Format headers to Title Case
    formatted_headers = [str(h).replace('_', ' ').title() for h in headers]
    
    table_data = [formatted_headers]
    
    for row in data:
        # Convert all values to string and truncate if too long
        row_data = [str(val)[:50] + ('...' if len(str(val)) > 50 else '') if val is not None else '' for val in row.values()]
        table_data.append(row_data)
        
    # Calculate column widths (divide page width evenly)
    page_width = landscape(letter)[0] - 60 # minus margins
    col_width = page_width / len(headers)
    
    t = Table(table_data, colWidths=[col_width] * len(headers))
    
    # Style the table
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a0a0f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4f6f9')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d4d8e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f4f6f9')]),
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    return buffer.getvalue()
