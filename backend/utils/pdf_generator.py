"""
TeleTrack Enterprise — PDF Generation Utility
Generates formatted PDF reports from tabular data.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_report(title, data):
    """
    Generate a professional A3 Landscape PDF report with intelligent column wrapping.
    """
    buffer = io.BytesIO()
    
    # Use A3 Landscape for maximum horizontal breathing room
    pagesize = landscape(A3)
    page_width, page_height = pagesize
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=pagesize,
        rightMargin=30, 
        leftMargin=30, 
        topMargin=40, 
        bottomMargin=40
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # ═══════════════════════════════ CUSTOM STYLES ═══════════════════════════════
    
    title_style = ParagraphStyle(
        name='CyberTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#00f0ff'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        name='CyberSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    cell_style = ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        wordWrap='LTR', 
    )
    
    header_style = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )

    # ═══════════════════════════════ DOCUMENT BODY ═══════════════════════════════

    def add_header_footer(canvas, doc):
        canvas.saveState()
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.gray)
        canvas.drawString(30, 20, f"TeleTrack Enterprise | Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.drawRightString(page_width - 30, 20, f"Page {doc.page}")
        canvas.restoreState()

    elements.append(Paragraph(f"TELETRACK ENTERPRISE: {title.upper()}", title_style))
    elements.append(Paragraph(f"SYSTEM AUDIT REPORT | {len(data)} RECORDS", subtitle_style))
    elements.append(Spacer(1, 10))
    
    if not data:
        elements.append(Paragraph("NO DATA RECORDS MATCHING CRITERIA FOUND.", styles['Normal']))
        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        return buffer.getvalue()

    headers = list(data[0].keys())
    num_cols = len(headers)
    
    # ═══════════════════════════════ SMART COLUMN WIDTHS ═══════════════════════════════
    
    # Total usable width = A3 Width - Margins (approx 1130 points)
    usable_width = page_width - 60
    
    col_widths = []
    # Identify "Heavy" columns that need wrapping
    heavy_cols = ['message', 'description', 'note', 'reason', 'summary', 'address', 'payload']
    medium_cols = ['device', 'name', 'title', 'subject', 'technician', 'email', 'website']
    
    for h in headers:
        h_low = h.lower()
        if any(x in h_low for x in heavy_cols):
            col_widths.append(usable_width * 0.25) # 25% for heavy text
        elif any(x in h_low for x in medium_cols):
            col_widths.append(usable_width * 0.15) # 15% for medium text
        elif h_low in ['id', 'status', 'priority', 'severity']:
            col_widths.append(usable_width * 0.08) # 8% for compact fields
        else:
            col_widths.append(None) # Auto-calculate later

    # Normalize assigned and remaining widths
    assigned_sum = sum([w for w in col_widths if w is not None])
    remaining_total = usable_width - assigned_sum
    auto_count = col_widths.count(None)
    
    final_widths = []
    for w in col_widths:
        if w is None:
            final_widths.append(remaining_total / auto_count if auto_count > 0 else usable_width/num_cols)
        else:
            final_widths.append(w)
            
    # Shrink fonts if we still have too many columns
    if num_cols > 10:
        cell_style.fontSize = 7
        cell_style.leading = 9
        header_style.fontSize = 8

    # ═══════════════════════════════ TABLE CONSTRUCTION ═══════════════════════════════

    # Formatted Header
    table_data = [[Paragraph(str(h).replace('_', ' ').upper(), header_style) for h in headers]]
    
    # Formatted Rows
    for row in data:
        row_cells = []
        for val in row.values():
            # Handle booleans and None properly
            if isinstance(val, bool):
                text = "YES" if val else "NO"
            else:
                text = str(val) if val is not None else "—"
            row_cells.append(Paragraph(text, cell_style))
        table_data.append(row_cells)
        
    t = Table(table_data, colWidths=final_widths, repeatRows=1)
    
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a0a0f')), # Deep space header
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')), # Subtle grid
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')]),
    ]))

    elements.append(t)
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    return buffer.getvalue()
