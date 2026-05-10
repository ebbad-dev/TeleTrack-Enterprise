"""
TeleTrack Enterprise — Dashboard Routes
Real-time dashboard summary metrics, chart data, alert trends, and SLA analytics.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Device, Alert, Technician, Incident, DeviceMetric, SLAPolicy
from utils.response import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_summary():
    """Get dashboard summary metrics."""
    try:
        total_devices = Device.query.filter_by(is_deleted=False).count()
        online_devices = Device.query.filter_by(status="online", is_deleted=False).count()
        offline_devices = Device.query.filter_by(status="offline", is_deleted=False).count()
        degraded_devices = Device.query.filter_by(status="degraded", is_deleted=False).count()

        open_alerts = Alert.query.filter(
            Alert.status.in_(["open", "assigned"]), Alert.is_deleted == False
        ).count()
        critical_alerts = Alert.query.filter(
            Alert.severity == "critical",
            Alert.status.in_(["open", "assigned"]),
            Alert.is_deleted == False,
        ).count()

        available_techs = Technician.query.filter_by(
            status="available", is_deleted=False
        ).count()
        total_techs = Technician.query.filter_by(is_deleted=False).count()

        open_incidents = Incident.query.filter(
            Incident.status.in_(["open", "acknowledged", "investigating"]),
            Incident.is_deleted == False,
        ).count()

        # SLA compliance
        total_with_sla = Alert.query.filter(
            Alert.sla_policy_id.isnot(None),
            Alert.is_deleted == False,
        ).count()
        sla_breached = Alert.query.filter(
            Alert.sla_breached == True,
            Alert.is_deleted == False,
        ).count()
        sla_compliance = (
            round(((total_with_sla - sla_breached) / total_with_sla) * 100)
            if total_with_sla > 0
            else 100
        )

        # Network health percentage
        health_pct = (
            round((online_devices / total_devices) * 100)
            if total_devices > 0
            else 0
        )

        # Average CPU/memory across online devices
        avg_cpu = db.session.query(db.func.avg(Device.cpu_usage)).filter(
            Device.status == "online", Device.is_deleted == False, Device.cpu_usage.isnot(None)
        ).scalar()
        avg_memory = db.session.query(db.func.avg(Device.memory_usage)).filter(
            Device.status == "online", Device.is_deleted == False, Device.memory_usage.isnot(None)
        ).scalar()

        data = {
            "total_devices": total_devices,
            "online_devices": online_devices,
            "offline_devices": offline_devices,
            "degraded_devices": degraded_devices,
            "open_alerts": open_alerts,
            "critical_alerts": critical_alerts,
            "available_technicians": available_techs,
            "total_technicians": total_techs,
            "open_incidents": open_incidents,
            "network_health": health_pct,
            "sla_compliance": sla_compliance,
            "sla_breached_count": sla_breached,
            "avg_cpu": round(avg_cpu, 1) if avg_cpu else 0,
            "avg_memory": round(avg_memory, 1) if avg_memory else 0,
        }

        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/alerts-by-severity", methods=["GET"])
@jwt_required()
def alerts_by_severity():
    """Get alert count grouped by severity."""
    try:
        results = (
            db.session.query(Alert.severity, db.func.count(Alert.id))
            .filter(Alert.status.in_(["open", "assigned"]), Alert.is_deleted == False)
            .group_by(Alert.severity)
            .all()
        )
        data = [{"severity": r[0], "count": r[1]} for r in results]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/devices-by-status", methods=["GET"])
@jwt_required()
def devices_by_status():
    """Get device count grouped by status."""
    try:
        results = (
            db.session.query(Device.status, db.func.count(Device.id))
            .filter(Device.is_deleted == False)
            .group_by(Device.status)
            .all()
        )
        data = [{"status": r[0], "count": r[1]} for r in results]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/recent-alerts", methods=["GET"])
@jwt_required()
def recent_alerts():
    """Get the 10 most recent alerts."""
    try:
        alerts = (
            Alert.query.filter_by(is_deleted=False)
            .order_by(Alert.alert_time.desc())
            .limit(10)
            .all()
        )
        return success_response([a.to_dict() for a in alerts])
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/devices-by-type", methods=["GET"])
@jwt_required()
def devices_by_type():
    """Get device count grouped by device type."""
    try:
        results = (
            db.session.query(Device.device_type, db.func.count(Device.id))
            .filter(Device.is_deleted == False)
            .group_by(Device.device_type)
            .all()
        )
        data = [{"device_type": r[0] or "Unknown", "count": r[1]} for r in results]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/alert-trends", methods=["GET"])
@jwt_required()
def alert_trends():
    """Get alert count per day for the last 30 days."""
    try:
        days = int(request.args.get("days", 30))
        since = datetime.now(timezone.utc) - timedelta(days=days)

        results = (
            db.session.query(
                db.func.date(Alert.alert_time),
                db.func.count(Alert.id),
            )
            .filter(Alert.alert_time >= since, Alert.is_deleted == False)
            .group_by(db.func.date(Alert.alert_time))
            .order_by(db.func.date(Alert.alert_time))
            .all()
        )

        data = [
            {"date": str(r[0]), "count": r[1]}
            for r in results
        ]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/incidents-by-severity", methods=["GET"])
@jwt_required()
def incidents_by_severity():
    """Get incident count grouped by severity."""
    try:
        results = (
            db.session.query(Incident.severity, db.func.count(Incident.id))
            .filter(
                Incident.status.in_(["open", "acknowledged", "investigating"]),
                Incident.is_deleted == False,
            )
            .group_by(Incident.severity)
            .all()
        )
        data = [{"severity": r[0], "count": r[1]} for r in results]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@dashboard_bp.route("/sla-metrics", methods=["GET"])
@jwt_required()
def sla_metrics():
    """Get SLA compliance metrics."""
    try:
        policies = SLAPolicy.query.all()
        metrics = []
        for policy in policies:
            total = Alert.query.filter(
                Alert.sla_policy_id == policy.id,
                Alert.is_deleted == False,
            ).count()
            breached = Alert.query.filter(
                Alert.sla_policy_id == policy.id,
                Alert.sla_breached == True,
                Alert.is_deleted == False,
            ).count()
            compliance = round(((total - breached) / total) * 100) if total > 0 else 100

            metrics.append({
                "severity": policy.severity_level,
                "total": total,
                "breached": breached,
                "compliant": total - breached,
                "compliance_pct": compliance,
                "response_time_minutes": policy.response_time_minutes,
                "resolution_time_minutes": policy.resolution_time_minutes,
            })

        return success_response(metrics)
    except Exception as e:
        return error_response(str(e))
