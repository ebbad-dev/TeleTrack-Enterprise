"""
TeleTrack Enterprise — Alert Routes
Full alert lifecycle with assignment, comments, and resolution.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Alert, AlertComment, AuditLog, Technician, SLAPolicy
from utils.response import success_response, error_response, paginated_response
from utils.pagination import paginate_query
from auth.decorators import permission_required
from auth.utils import current_user_id

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@alerts_bp.route("", methods=["GET"])
@jwt_required()
def get_alerts():
    """Get alerts with filtering and pagination."""
    try:
        query = Alert.query.filter_by(is_deleted=False)
        status = request.args.get("status")
        severity = request.args.get("severity")
        device_id = request.args.get("device_id", type=int)
        search = request.args.get("search", "").strip()

        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        if device_id:
            query = query.filter(Alert.device_id == device_id)
        if search:
            query = query.filter(
                db.or_(
                    Alert.alert_type.ilike(f"%{search}%"),
                    Alert.message.ilike(f"%{search}%"),
                )
            )
        query = query.order_by(Alert.alert_time.desc())
        items, total, page, per_page = paginate_query(query)
        return paginated_response([a.to_dict() for a in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))


@alerts_bp.route("/<int:alert_id>", methods=["GET"])
@jwt_required()
def get_alert(alert_id):
    try:
        alert = Alert.query.filter_by(id=alert_id, is_deleted=False).first()
        if not alert:
            return error_response("Alert not found", 404)
        data = alert.to_dict()
        comments = AlertComment.query.filter_by(alert_id=alert_id).order_by(AlertComment.commented_at.desc()).all()
        data["comments"] = [c.to_dict() for c in comments]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@alerts_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("alerts:write")
def create_alert():
    try:
        data = request.get_json()
        if not data or not data.get("device_id"):
            return error_response("device_id is required", 400)

        alert = Alert(
            device_id=data["device_id"],
            alert_type=data.get("alert_type", "Manual Alert"),
            severity=data.get("severity", "medium"),
            message=data.get("message"),
            status="open",
            priority=data.get("priority", 3),
            created_by_id=current_user_id(),
        )
        sla = SLAPolicy.query.filter_by(severity_level=alert.severity).first()
        if sla:
            alert.sla_policy_id = sla.id
            alert.sla_response_deadline = datetime.now(timezone.utc) + timedelta(minutes=sla.response_time_minutes)
            alert.sla_resolution_deadline = datetime.now(timezone.utc) + timedelta(minutes=sla.resolution_time_minutes)

        db.session.add(alert)
        db.session.commit()
        return success_response(alert.to_dict(), "Alert created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@alerts_bp.route("/<int:alert_id>/assign", methods=["POST"])
@jwt_required()
@permission_required("alerts:assign")
def assign_alert(alert_id):
    try:
        alert = Alert.query.filter_by(id=alert_id, is_deleted=False).first()
        if not alert:
            return error_response("Alert not found", 404)
        data = request.get_json()
        tech_id = data.get("technician_id")
        if not tech_id:
            return error_response("technician_id is required", 400)
        tech = Technician.query.filter_by(id=tech_id, is_deleted=False).first()
        if not tech:
            return error_response("Technician not found", 404)

        alert.assigned_tech_id = tech_id
        alert.status = "assigned"
        tech.total_alerts = (tech.total_alerts or 0) + 1

        db.session.add(AlertComment(alert_id=alert_id, user_id=current_user_id(), comment=f"Assigned to {tech.full_name}", comment_type="update"))
        db.session.add(AuditLog(user_id=current_user_id(), action="ALERT_ASSIGNED", resource="alerts", resource_id=alert_id, new_value=f"Assigned to {tech.full_name}", ip_address=request.remote_addr))
        db.session.commit()
        return success_response(alert.to_dict(), "Alert assigned successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@alerts_bp.route("/<int:alert_id>/resolve", methods=["POST"])
@jwt_required()
@permission_required("alerts:resolve")
def resolve_alert(alert_id):
    try:
        alert = Alert.query.filter_by(id=alert_id, is_deleted=False).first()
        if not alert:
            return error_response("Alert not found", 404)
        data = request.get_json() or {}
        note = data.get("resolution_note", "")

        alert.status = "resolved"
        alert.resolved_time = datetime.now(timezone.utc)
        alert.resolution_note = note
        alert.resolved_by_id = current_user_id()

        if alert.assigned_tech_id:
            tech = Technician.query.get(alert.assigned_tech_id)
            if tech:
                tech.resolved_alerts = (tech.resolved_alerts or 0) + 1

        db.session.add(AlertComment(alert_id=alert_id, user_id=current_user_id(), comment=note or "Alert resolved", comment_type="resolution"))
        db.session.add(AuditLog(user_id=current_user_id(), action="ALERT_RESOLVED", resource="alerts", resource_id=alert_id, new_value=note, ip_address=request.remote_addr))
        db.session.commit()
        return success_response(alert.to_dict(), "Alert resolved")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@alerts_bp.route("/<int:alert_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(alert_id):
    try:
        comments = AlertComment.query.filter_by(alert_id=alert_id).order_by(AlertComment.commented_at.desc()).all()
        return success_response([c.to_dict() for c in comments])
    except Exception as e:
        return error_response(str(e))


@alerts_bp.route("/<int:alert_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(alert_id):
    try:
        data = request.get_json()
        if not data or not data.get("comment"):
            return error_response("Comment text is required", 400)
        comment = AlertComment(alert_id=alert_id, user_id=current_user_id(), comment=data["comment"], comment_type=data.get("comment_type", "note"))
        db.session.add(comment)
        db.session.commit()
        return success_response(comment.to_dict(), "Comment added", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))
