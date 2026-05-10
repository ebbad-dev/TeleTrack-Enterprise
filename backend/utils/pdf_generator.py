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
    Generate a beautiful, responsive PDF report with text wrapping.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter),
        rightMargin=20, 
        leftMargin=20, 
        topMargin=30, 
        bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#00f0ff'),
        spaceAfter=15,
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        spaceAfter=20,
        alignment=1
    )

    cell_style = ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        wordWrap='CJK', # Good for long text
    )
    
    header_style = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold',
    )

    elements.append(Paragraph(f"TeleTrack Enterprise: {title}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    
    if not data:
        elements.append(Paragraph("No data available.", styles['Normal']))
        doc.build(elements)
        return buffer.getvalue()

    headers = list(data[0].keys())
    num_cols = len(headers)
    
    # Header row
    table_data = [[Paragraph(str(h).replace('_', ' ').title(), header_style) for h in headers]]
    
    # Body rows
    for row in data:
        row_cells = []
        for val in row.values():
            text = str(val) if val is not None else ""
            row_cells.append(Paragraph(text, cell_style))
        table_data.append(row_cells)
        
    # Calculate widths intelligently
    page_width = landscape(letter)[0] - 40
    # Give 'Message' or 'Title' or 'Description' more space if they exist
    col_widths = []
    for h in headers:
        h_lower = h.lower()
        if any(x in h_lower for x in ['message', 'description', 'note', 'title', 'reason']):
            col_widths.append(page_width * 0.2) # 20% for long text fields
        else:
            col_widths.append(None) # Auto-calculate the rest
            
    # Normalize widths
    assigned_width = sum([w for w in col_widths if w is not None])
    remaining_width = (page_width - assigned_width)
    remaining_cols = col_widths.count(None)
    
    final_widths = []
    for w in col_widths:
        if w is None:
            final_widths.append(remaining_width / remaining_cols)
        else:
            final_widths.append(w)
            
    # Adjust font size if too many columns
    if num_cols > 10:
        cell_style.fontSize = 7
        cell_style.leading = 8
        header_style.fontSize = 8

    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a0a0f')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d4d8e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f7f9fc')]),
    ]))

    elements.append(t)
    doc.build(elements)
    
    return buffer.getvalue()
