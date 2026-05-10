"""
TeleTrack Enterprise — Export Routes
CSV export endpoints for devices, alerts, incidents, and audit logs.
"""

import csv
import io
from flask import Blueprint, Response, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Device, Alert, Incident, AuditLog, Technician, Location
from auth.decorators import permission_required

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


def generate_csv(headers, rows):
    """Generate a CSV string from headers and rows."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()


@export_bp.route("/devices", methods=["GET"])
@jwt_required()
def export_devices():
    """Export all devices as CSV."""
    try:
        devices = Device.query.filter_by(is_deleted=False).order_by(Device.device_name).all()
        headers = [
            "ID", "Device Name", "Type", "IP Address", "MAC Address",
            "Status", "Vendor", "Model", "Location", "Serial Number",
            "Firmware", "Installed Date", "Warranty Expiry",
            "CPU %", "Memory %", "Temperature", "Uptime (hrs)", "Created At"
        ]
        rows = []
        for d in devices:
            rows.append([
                d.id, d.device_name, d.device_type, d.ip_address, d.mac_address,
                d.status, d.vendor.vendor_name if d.vendor else "",
                d.model, d.location.location_name if d.location else "",
                d.serial_number, d.firmware_version,
                d.installed_date.isoformat() if d.installed_date else "",
                d.warranty_expiry.isoformat() if d.warranty_expiry else "",
                d.cpu_usage, d.memory_usage, d.temperature, d.uptime,
                d.created_at.isoformat() if d.created_at else "",
            ])

        csv_data = generate_csv(headers, rows)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=teletrack_devices.csv"},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/alerts", methods=["GET"])
@jwt_required()
def export_alerts():
    """Export alerts as CSV."""
    try:
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
        for a in alerts:
            rows.append([
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
            ])

        csv_data = generate_csv(headers, rows)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=teletrack_alerts.csv"},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/incidents", methods=["GET"])
@jwt_required()
def export_incidents():
    """Export incidents as CSV."""
    try:
        incidents = Incident.query.filter_by(is_deleted=False).order_by(Incident.reported_at.desc()).all()
        headers = [
            "ID", "Title", "Severity", "Status", "Priority", "Impact",
            "Reported By", "Assigned To", "Reported At",
            "Acknowledged At", "Resolved At", "Closed At",
            "SLA Breached", "Root Cause", "Resolution Summary"
        ]
        rows = []
        for i in incidents:
            rows.append([
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
            ])

        csv_data = generate_csv(headers, rows)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=teletrack_incidents.csv"},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@export_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@permission_required("audit:read")
def export_audit_logs():
    """Export audit logs as CSV."""
    try:
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(1000).all()
        headers = [
            "ID", "User", "Action", "Resource", "Resource ID",
            "Old Value", "New Value", "IP Address", "Timestamp"
        ]
        rows = []
        for l in logs:
            rows.append([
                l.id,
                l.user.full_name if l.user else "System",
                l.action, l.resource, l.resource_id,
                l.old_value or "", l.new_value or "",
                l.ip_address,
                l.timestamp.isoformat() if l.timestamp else "",
            ])

        csv_data = generate_csv(headers, rows)
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=teletrack_audit_logs.csv"},
        )
    except Exception as e:
        return {"success": False, "error": str(e)}, 500
