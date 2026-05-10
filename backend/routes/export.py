"""
TeleTrack Enterprise — Export Routes
CSV, PDF, Excel, and TXT export endpoints for devices, alerts, incidents, and audit logs.
"""

import csv
import io
import openpyxl
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Device, Alert, Incident, AuditLog, Technician, Location
from auth.decorators import permission_required
from utils.pdf_generator import generate_pdf_report

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


def generate_csv(headers, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


def generate_txt(headers, rows):
    output = io.StringIO()
    output.write("TELETRACK ENTERPRISE REPORT\n")
    output.write("=" * 80 + "\n\n")
    output.write(" | ".join(headers) + "\n")
    output.write("-" * 80 + "\n")
    for row in rows:
        output.write(" | ".join([str(item) for item in row]) + "\n")
    return output.getvalue()


def generate_xlsx(headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def handle_export(format_type, filename_base, title, headers, rows, dict_data):
    """Helper to route the export request to the correct generator."""
    if format_type == 'pdf':
        pdf_data = generate_pdf_report(title, dict_data)
        return Response(
            pdf_data,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.pdf"},
        )
    elif format_type == 'xlsx':
        xlsx_data = generate_xlsx(headers, rows)
        return Response(
            xlsx_data,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.xlsx"},
        )
    elif format_type == 'txt':
        txt_data = generate_txt(headers, rows)
        return Response(
            txt_data,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.txt"},
        )
    else:  # default csv
        csv_data = generate_csv(headers, rows)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"},
        )


@export_bp.route("/devices", methods=["GET"])
@jwt_required()
def export_devices():
    """Export all devices."""
    try:
        format_type = request.args.get("format", "csv").lower()
        devices = Device.query.filter_by(is_deleted=False).order_by(Device.device_name).all()
        
        headers = [
            "ID", "Device Name", "Type", "IP Address", "MAC Address",
            "Status", "Vendor", "Model", "Location", "Serial Number",
            "Firmware", "Installed Date", "Warranty Expiry",
            "CPU %", "Memory %", "Temperature", "Uptime (hrs)", "Created At"
        ]
        rows = []
        dict_data = []
        
        for d in devices:
            row = [
                d.id, d.device_name, d.device_type, d.ip_address, d.mac_address,
                d.status, d.vendor.vendor_name if d.vendor else "",
                d.model, d.location.location_name if d.location else "",
                d.serial_number, d.firmware_version,
                d.installed_date.isoformat() if d.installed_date else "",
                d.warranty_expiry.isoformat() if d.warranty_expiry else "",
                d.cpu_usage, d.memory_usage, d.temperature, d.uptime,
                d.created_at.isoformat() if d.created_at else "",
            ]
            rows.append(row)
            dict_data.append(dict(zip(headers, row)))

        return handle_export(format_type, "teletrack_devices", "Network Devices Report", headers, rows, dict_data)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/alerts", methods=["GET"])
@jwt_required()
def export_alerts():
    """Export alerts."""
    try:
        format_type = request.args.get("format", "csv").lower()
        query = Alert.query.filter_by(is_deleted=False).order_by(Alert.alert_time.desc())
        status = request.args.get("status")
        severity = request.args.get("severity")
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)

        alerts = query.all()
        headers = [
            "ID", "Device", "Type", "Severity", "Status", "Priority",
            "Message", "Alert Time", "Acknowledged At", "Resolved Time",
            "Technician", "SLA Breached", "Resolution Note"
        ]
        rows = []
        dict_data = []
        
        for a in alerts:
            row = [
                a.id,
                a.device.device_name if a.device else "",
                a.alert_type, a.severity, a.status, a.priority,
                a.message,
                a.alert_time.isoformat() if a.alert_time else "",
                a.acknowledged_at.isoformat() if a.acknowledged_at else "",
                a.resolved_time.isoformat() if a.resolved_time else "",
                a.assigned_tech.full_name if a.assigned_tech else "Unassigned",
                "Yes" if a.sla_breached else "No",
                a.resolution_note or "",
            ]
            rows.append(row)
            dict_data.append(dict(zip(headers, row)))

        return handle_export(format_type, "teletrack_alerts", "Active Threat Report", headers, rows, dict_data)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/incidents", methods=["GET"])
@jwt_required()
def export_incidents():
    """Export incidents."""
    try:
        format_type = request.args.get("format", "csv").lower()
        incidents = Incident.query.filter_by(is_deleted=False).order_by(Incident.reported_at.desc()).all()
        
        headers = [
            "ID", "Title", "Severity", "Status", "Priority", "Impact",
            "Reported By", "Assigned To", "Reported At",
            "Acknowledged At", "Resolved At", "Closed At",
            "SLA Breached", "Root Cause", "Resolution Summary"
        ]
        rows = []
        dict_data = []
        
        for i in incidents:
            row = [
                i.id, i.title, i.severity, i.status, i.priority, i.impact,
                i.reported_by.full_name if i.reported_by else "",
                i.assigned_to.full_name if i.assigned_to else "",
                i.reported_at.isoformat() if i.reported_at else "",
                i.acknowledged_at.isoformat() if i.acknowledged_at else "",
                i.resolved_at.isoformat() if i.resolved_at else "",
                i.closed_at.isoformat() if i.closed_at else "",
                "Yes" if i.sla_breached else "No",
                i.root_cause or "",
                i.resolution_summary or "",
            ]
            rows.append(row)
            dict_data.append(dict(zip(headers, row)))

        return handle_export(format_type, "teletrack_incidents", "Major Incident Report", headers, rows, dict_data)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@permission_required("audit:read")
def export_audit_logs():
    """Export audit logs."""
    try:
        format_type = request.args.get("format", "csv").lower()
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(1000).all()
        
        headers = [
            "ID", "User", "Action", "Resource", "Resource ID",
            "Old Value", "New Value", "IP Address", "Timestamp"
        ]
        rows = []
        dict_data = []
        
        for l in logs:
            row = [
                l.id,
                l.user.full_name if l.user else "System",
                l.action, l.resource, l.resource_id,
                l.old_value or "", l.new_value or "",
                l.ip_address,
                l.timestamp.isoformat() if l.timestamp else "",
            ]
            rows.append(row)
            dict_data.append(dict(zip(headers, row)))

        return handle_export(format_type, "teletrack_audit_logs", "Security Audit Log", headers, rows, dict_data)
    except Exception as e:
        return {"success": False, "error": str(e)}, 500
