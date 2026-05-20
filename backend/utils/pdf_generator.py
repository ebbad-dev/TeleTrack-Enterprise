"""
TeleTrack Enterprise — PDF Generation Utility
Generates professional, branded PDF reports with intelligent layout.
Fixed: text overlapping, column overflow, pagination issues.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ═══════════════════════════════════════════════════════════════════
# Color Palette — Cyberpunk Enterprise Theme
# ═══════════════════════════════════════════════════════════════════

COLORS = {
    "bg_dark": colors.HexColor("#0a0a0f"),
    "bg_header": colors.HexColor("#0d1117"),
    "bg_row_even": colors.HexColor("#ffffff"),
    "bg_row_odd": colors.HexColor("#f6f8fa"),
    "accent": colors.HexColor("#00b4d8"),
    "accent_dark": colors.HexColor("#0077b6"),
    "text_header": colors.HexColor("#e0e0e0"),
    "text_body": colors.HexColor("#1a1d2e"),
    "text_muted": colors.HexColor("#6b7085"),
    "border": colors.HexColor("#d0d7de"),
    "border_light": colors.HexColor("#e8ecf0"),
    "success": colors.HexColor("#2da44e"),
    "warning": colors.HexColor("#d29922"),
    "error": colors.HexColor("#cf222e"),
}


def _build_styles():
    """Create all paragraph styles used in the report."""
    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "TT_Title", parent=styles["Heading1"],
            fontSize=24, textColor=COLORS["accent"],
            spaceAfter=6, alignment=TA_CENTER,
            fontName="Helvetica-Bold", leading=28,
        ),
        "subtitle": ParagraphStyle(
            "TT_Subtitle", parent=styles["Normal"],
            fontSize=11, textColor=COLORS["text_muted"],
            spaceAfter=20, alignment=TA_CENTER,
            fontName="Helvetica",
        ),
        "section": ParagraphStyle(
            "TT_Section", parent=styles["Heading2"],
            fontSize=14, textColor=COLORS["accent_dark"],
            spaceBefore=16, spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "summary_label": ParagraphStyle(
            "TT_SumLabel", parent=styles["Normal"],
            fontSize=9, textColor=COLORS["text_muted"],
            fontName="Helvetica",
        ),
        "summary_value": ParagraphStyle(
            "TT_SumValue", parent=styles["Normal"],
            fontSize=12, textColor=COLORS["text_body"],
            fontName="Helvetica-Bold",
        ),
        "header_cell": ParagraphStyle(
            "TT_HeaderCell", parent=styles["Normal"],
            fontSize=8, leading=10,
            textColor=COLORS["text_header"],
            fontName="Helvetica-Bold", alignment=TA_LEFT,
        ),
        "body_cell": ParagraphStyle(
            "TT_BodyCell", parent=styles["Normal"],
            fontSize=8, leading=10,
            textColor=COLORS["text_body"],
            fontName="Helvetica", wordWrap="LTR",
        ),
        "body_cell_small": ParagraphStyle(
            "TT_BodyCellSm", parent=styles["Normal"],
            fontSize=7, leading=9,
            textColor=COLORS["text_body"],
            fontName="Helvetica", wordWrap="LTR",
        ),
        "footer": ParagraphStyle(
            "TT_Footer", parent=styles["Normal"],
            fontSize=8, textColor=COLORS["text_muted"],
            fontName="Helvetica",
        ),
    }


def _calculate_column_widths(headers, usable_width):
    """
    Intelligently distribute column widths based on header content.
    Heavy-text columns get more space; compact fields get less.
    """
    heavy_keywords = ["message", "description", "note", "reason",
                      "summary", "address", "payload", "services",
                      "resolution", "lessons", "root_cause", "agent"]
    medium_keywords = ["device", "name", "title", "subject",
                       "technician", "email", "website", "user"]
    compact_keywords = ["id", "status", "priority", "severity",
                        "type", "sla", "breached", "outcome"]

    num_cols = len(headers)

    # Assign weight factors
    weights = []
    for h in headers:
        h_low = h.lower().replace(" ", "_")
        if any(k in h_low for k in heavy_keywords):
            weights.append(4.0)
        elif any(k in h_low for k in medium_keywords):
            weights.append(2.5)
        elif any(k in h_low for k in compact_keywords):
            weights.append(1.0)
        else:
            weights.append(1.8)

    total_weight = sum(weights)
    widths = [(w / total_weight) * usable_width for w in weights]

    # Enforce minimum width of 35pt per column
    min_width = 35
    for i in range(len(widths)):
        if widths[i] < min_width:
            widths[i] = min_width

    # Re-normalize to fit page
    current_total = sum(widths)
    if current_total > usable_width:
        scale = usable_width / current_total
        widths = [w * scale for w in widths]

    return widths


def _format_cell_value(val):
    """Convert a value to a clean display string."""
    if val is None:
        return "—"
    if isinstance(val, bool):
        return "Yes" if val else "No"
    text = str(val).strip()
    # Truncate extremely long values to prevent layout issues
    if len(text) > 200:
        text = text[:197] + "..."
    return text if text else "—"


def _add_header_footer(canvas, doc, title, page_width):
    """Draw branded header and footer on every page."""
    canvas.saveState()

    # ── Footer ──
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLORS["text_muted"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    canvas.drawString(
        30, 18,
        f"TeleTrack Enterprise  •  {title}  •  Generated: {timestamp}"
    )
    canvas.drawRightString(
        page_width - 30, 18,
        f"Page {doc.page}"
    )

    # ── Top line accent ──
    canvas.setStrokeColor(COLORS["accent"])
    canvas.setLineWidth(2)
    canvas.line(30, doc.pagesize[1] - 20, page_width - 30, doc.pagesize[1] - 20)

    canvas.restoreState()


def generate_pdf_report(title, data):
    """
    Generate a professional branded PDF report.

    Args:
        title: Report title string
        data: List of dicts (each dict is one row)

    Returns:
        bytes: PDF file content
    """
    buffer = io.BytesIO()
    pagesize = landscape(A3)
    page_width, page_height = pagesize

    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=30, leftMargin=30,
        topMargin=45, bottomMargin=40,
    )

    styles = _build_styles()
    elements = []

    # ═══════════════════════════════════════════════════════════════
    # Title Block
    # ═══════════════════════════════════════════════════════════════

    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(f"TELETRACK ENTERPRISE", styles["title"])
    )
    elements.append(
        Paragraph(f"{title.upper()}", styles["section"])
    )
    elements.append(
        Paragraph(
            f"System Audit Report  •  {len(data)} Records  •  "
            f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            styles["subtitle"],
        )
    )

    # Separator
    elements.append(
        HRFlowable(
            width="100%", thickness=1,
            color=COLORS["border_light"],
            spaceAfter=15, spaceBefore=5,
        )
    )

    # ═══════════════════════════════════════════════════════════════
    # Summary Stats Bar
    # ═══════════════════════════════════════════════════════════════

    if data:
        # Count unique statuses/severities if present
        summary_items = [("Total Records", str(len(data)))]

        sample_keys = [k.lower() for k in data[0].keys()]
        if "status" in sample_keys:
            statuses = {}
            for row in data:
                s = str(row.get("Status", row.get("status", "Unknown")))
                statuses[s] = statuses.get(s, 0) + 1
            for status, count in sorted(statuses.items(), key=lambda x: -x[1])[:4]:
                summary_items.append((status.title(), str(count)))

        if "severity" in sample_keys:
            severities = {}
            for row in data:
                s = str(row.get("Severity", row.get("severity", "Unknown")))
                severities[s] = severities.get(s, 0) + 1
            for sev, count in sorted(severities.items(), key=lambda x: -x[1])[:4]:
                summary_items.append((f"{sev.title()} Severity", str(count)))

        # Build summary table (horizontal)
        if len(summary_items) > 1:
            summary_row_labels = [
                Paragraph(item[0].upper(), styles["summary_label"])
                for item in summary_items[:6]
            ]
            summary_row_values = [
                Paragraph(item[1], styles["summary_value"])
                for item in summary_items[:6]
            ]
            num_summary = len(summary_row_labels)
            summary_width = (page_width - 60) / num_summary

            summary_table = Table(
                [summary_row_values, summary_row_labels],
                colWidths=[summary_width] * num_summary,
            )
            summary_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f4f8")),
                ("BOX", (0, 0), (-1, -1), 0.5, COLORS["border_light"]),
                ("LINEAFTER", (0, 0), (-2, -1), 0.5, COLORS["border_light"]),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

    # ═══════════════════════════════════════════════════════════════
    # Data Table
    # ═══════════════════════════════════════════════════════════════

    if not data:
        elements.append(
            Paragraph(
                "No data records matching the specified criteria were found.",
                styles["body_cell"],
            )
        )
        doc.build(
            elements,
            onFirstPage=lambda c, d: _add_header_footer(c, d, title, page_width),
            onLaterPages=lambda c, d: _add_header_footer(c, d, title, page_width),
        )
        return buffer.getvalue()

    headers = list(data[0].keys())
    num_cols = len(headers)
    usable_width = page_width - 60

    col_widths = _calculate_column_widths(headers, usable_width)

    # Choose cell style based on column density
    cell_style = styles["body_cell_small"] if num_cols > 12 else styles["body_cell"]
    header_style = styles["header_cell"]

    # ── Format header row ──
    formatted_headers = [
        Paragraph(str(h).replace("_", " ").upper(), header_style)
        for h in headers
    ]

    # ── Format data rows ──
    table_data = [formatted_headers]
    for row in data:
        formatted_row = []
        for val in row.values():
            text = _format_cell_value(val)
            # Wrap in Paragraph for automatic text wrapping
            formatted_row.append(Paragraph(text, cell_style))
        table_data.append(formatted_row)

    # ── Build table ──
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header styling
        ("BACKGROUND", (0, 0), (-1, 0), COLORS["bg_header"]),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLORS["text_header"]),

        # Cell alignment and padding
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),

        # Grid lines
        ("GRID", (0, 0), (-1, 0), 0.5, COLORS["accent_dark"]),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, COLORS["accent"]),
        ("GRID", (0, 1), (-1, -1), 0.3, COLORS["border_light"]),

        # Alternating row colors
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [COLORS["bg_row_even"], COLORS["bg_row_odd"]]),
    ]))

    elements.append(table)

    # ═══════════════════════════════════════════════════════════════
    # Build PDF
    # ═══════════════════════════════════════════════════════════════

    doc.build(
        elements,
        onFirstPage=lambda c, d: _add_header_footer(c, d, title, page_width),
        onLaterPages=lambda c, d: _add_header_footer(c, d, title, page_width),
    )

    return buffer.getvalue()
