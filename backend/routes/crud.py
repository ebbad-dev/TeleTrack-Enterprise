"""
TeleTrack Enterprise — Generic CRUD Routes
Technicians, Locations, Vendors, Maintenance, Network Links, SLA, Audit, Incidents, Notifications, Search, Dropdowns.
"""

from datetime import datetime, timezone
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import (
    Technician, Location, Vendor, MaintenanceLog, NetworkLink, SLAPolicy,
    AuditLog, Incident, IncidentTimeline, Notification, Device, Alert,
)
from utils.response import success_response, error_response, paginated_response
from utils.pagination import paginate_query
from auth.decorators import permission_required, admin_required
from auth.utils import current_user_id

# ═══════════════════════════════ TECHNICIANS ═══════════════════════════════

technicians_bp = Blueprint("technicians", __name__, url_prefix="/api/technicians")

@technicians_bp.route("", methods=["GET"])
@jwt_required()
def get_technicians():
    try:
        query = Technician.query.filter_by(is_deleted=False).order_by(Technician.full_name)
        status = request.args.get("status")
        if status:
            query = query.filter(Technician.status == status)
        items, total, page, per_page = paginate_query(query, default_per_page=50)
        return paginated_response([t.to_dict() for t in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@technicians_bp.route("/<int:tid>", methods=["GET"])
@jwt_required()
def get_technician(tid):
    try:
        t = Technician.query.filter_by(id=tid, is_deleted=False).first()
        if not t:
            return error_response("Technician not found", 404)
        data = t.to_dict()
        assigned = Alert.query.filter_by(assigned_tech_id=tid, is_deleted=False).filter(Alert.status.in_(["assigned","in_progress"])).count()
        data["active_alerts"] = assigned
        return success_response(data)
    except Exception as e:
        return error_response(str(e))

@technicians_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("technicians:write")
def create_technician():
    try:
        data = request.get_json()
        if not data or not data.get("full_name"):
            return error_response("full_name is required", 400)
        t = Technician(full_name=data["full_name"], email=data.get("email"), phone=data.get("phone"),
                       specialization=data.get("specialization"), shift=data.get("shift", "Flexible"),
                       status=data.get("status", "available"), image_url=data.get("image_url"))
        db.session.add(t)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="technicians", action_type="CREATE", name=t.full_name)
        return success_response(t.to_dict(), "Technician created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@technicians_bp.route("/<int:tid>", methods=["PUT"])
@jwt_required()
@permission_required("technicians:write")
def update_technician(tid):
    try:
        t = Technician.query.filter_by(id=tid, is_deleted=False).first()
        if not t:
            return error_response("Technician not found", 404)
        data = request.get_json()
        for f in ["full_name","email","phone","specialization","shift","status","image_url"]:
            if f in data:
                setattr(t, f, data[f])
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="technicians", action_type="UPDATE", name=t.full_name)
        return success_response(t.to_dict(), "Technician updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@technicians_bp.route("/<int:tid>", methods=["DELETE"])
@jwt_required()
@permission_required("technicians:delete")
def delete_technician(tid):
    try:
        t = Technician.query.filter_by(id=tid, is_deleted=False).first()
        if not t:
            return error_response("Technician not found", 404)
        t.soft_delete()
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="technicians", action_type="DELETE", name=t.full_name)
        return success_response(message="Technician deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ LOCATIONS ═══════════════════════════════

locations_bp = Blueprint("locations", __name__, url_prefix="/api/locations")

@locations_bp.route("", methods=["GET"])
@jwt_required()
def get_locations():
    try:
        query = Location.query.filter_by(is_deleted=False).order_by(Location.location_name)
        items, total, page, per_page = paginate_query(query, default_per_page=50)
        
        serialized_items = []
        for l in items:
            try:
                serialized_items.append(l.to_dict())
            except Exception as e:
                print(f"CRITICAL ERROR serializing location {l.id}: {str(e)}")
                raise e
                
        return paginated_response(serialized_items, total, page, per_page)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(str(e))

@locations_bp.route("/<int:lid>", methods=["GET"])
@jwt_required()
def get_location(lid):
    try:
        loc = Location.query.filter_by(id=lid, is_deleted=False).first()
        if not loc:
            return error_response("Location not found", 404)
        return success_response(loc.to_dict())
    except Exception as e:
        return error_response(str(e))

@locations_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("locations:write")
def create_location():
    try:
        data = request.get_json()
        if not data or not data.get("location_name"):
            return error_response("location_name is required", 400)
        loc = Location(location_name=data["location_name"], city=data.get("city"), country=data.get("country"),
                       site_type=data.get("site_type"), address_line=data.get("address_line"),
                       contact_person=data.get("contact_person"), contact_phone=data.get("contact_phone"),
                       image_url=data.get("image_url"))
        db.session.add(loc)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="locations", action_type="CREATE", name=loc.location_name)
        return success_response(loc.to_dict(), "Location created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@locations_bp.route("/<int:lid>", methods=["PUT"])
@jwt_required()
@permission_required("locations:write")
def update_location(lid):
    try:
        loc = Location.query.filter_by(id=lid, is_deleted=False).first()
        if not loc:
            return error_response("Location not found", 404)
        data = request.get_json()
        for f in ["location_name","city","country","site_type","address_line","contact_person","contact_phone","image_url"]:
            if f in data:
                setattr(loc, f, data[f])
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="locations", action_type="UPDATE", name=loc.location_name)
        return success_response(loc.to_dict(), "Location updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@locations_bp.route("/<int:lid>", methods=["DELETE"])
@jwt_required()
@permission_required("locations:delete")
def delete_location(lid):
    try:
        loc = Location.query.filter_by(id=lid, is_deleted=False).first()
        if not loc:
            return error_response("Location not found", 404)
        loc.soft_delete()
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="locations", action_type="DELETE", name=loc.location_name)
        return success_response(message="Location deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ VENDORS ═══════════════════════════════

vendors_bp = Blueprint("vendors", __name__, url_prefix="/api/vendors")

@vendors_bp.route("", methods=["GET"])
@jwt_required()
def get_vendors():
    try:
        query = Vendor.query.filter_by(is_deleted=False).order_by(Vendor.vendor_name)
        items, total, page, per_page = paginate_query(query, default_per_page=50)
        return paginated_response([v.to_dict() for v in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@vendors_bp.route("/<int:vid>", methods=["GET"])
@jwt_required()
def get_vendor(vid):
    try:
        v = Vendor.query.filter_by(id=vid, is_deleted=False).first()
        if not v:
            return error_response("Vendor not found", 404)
        return success_response(v.to_dict())
    except Exception as e:
        return error_response(str(e))

@vendors_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("vendors:write")
def create_vendor():
    try:
        data = request.get_json()
        if not data or not data.get("vendor_name"):
            return error_response("vendor_name is required", 400)
        v = Vendor(vendor_name=data["vendor_name"], country_of_origin=data.get("country_of_origin"),
                   support_email=data.get("support_email"), support_phone=data.get("support_phone"),
                   website=data.get("website"))
        db.session.add(v)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="vendors", action_type="CREATE", name=v.vendor_name)
        return success_response(v.to_dict(), "Vendor created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@vendors_bp.route("/<int:vid>", methods=["PUT"])
@jwt_required()
@permission_required("vendors:write")
def update_vendor(vid):
    try:
        v = Vendor.query.filter_by(id=vid, is_deleted=False).first()
        if not v:
            return error_response("Vendor not found", 404)
        data = request.get_json()
        for f in ["vendor_name","country_of_origin","support_email","support_phone","website"]:
            if f in data:
                setattr(v, f, data[f])
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="vendors", action_type="UPDATE", name=v.vendor_name)
        return success_response(v.to_dict(), "Vendor updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@vendors_bp.route("/<int:vid>", methods=["DELETE"])
@jwt_required()
@permission_required("vendors:delete")
def delete_vendor(vid):
    try:
        v = Vendor.query.filter_by(id=vid, is_deleted=False).first()
        if not v:
            return error_response("Vendor not found", 404)
        v.soft_delete()
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="vendors", action_type="DELETE", name=v.vendor_name)
        return success_response(message="Vendor deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ MAINTENANCE ═══════════════════════════════

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")

@maintenance_bp.route("", methods=["GET"])
@jwt_required()
def get_maintenance():
    try:
        query = MaintenanceLog.query.order_by(MaintenanceLog.created_at.desc())
        items, total, page, per_page = paginate_query(query)
        return paginated_response([m.to_dict() for m in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@maintenance_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("maintenance:write")
def create_maintenance():
    try:
        data = request.get_json()
        if not data or not data.get("device_id"):
            return error_response("device_id is required", 400)
        m = MaintenanceLog(device_id=data["device_id"], technician_id=data.get("technician_id"),
                           maintenance_type=data.get("maintenance_type", "Preventive"),
                           description=data.get("description"), scheduled_date=data.get("scheduled_date"),
                           completed_date=data.get("completed_date"), duration_minutes=data.get("duration_minutes"),
                           outcome=data.get("outcome"), notes=data.get("notes"), image_url=data.get("image_url"))
        db.session.add(m)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="maintenance", action_type="CREATE", name=f"Task #{m.id} ({m.maintenance_type})")
        return success_response(m.to_dict(), "Maintenance log created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@maintenance_bp.route("/<int:mid>", methods=["PUT"])
@jwt_required()
@permission_required("maintenance:write")
def update_maintenance(mid):
    try:
        m = MaintenanceLog.query.get(mid)
        if not m:
            return error_response("Maintenance log not found", 404)
        data = request.get_json()
        for f in ["device_id","technician_id","maintenance_type","description","scheduled_date",
                   "completed_date","duration_minutes","outcome","notes","image_url"]:
            if f in data:
                setattr(m, f, data[f])
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="maintenance", action_type="UPDATE", name=f"Task #{m.id} ({m.maintenance_type})")
        return success_response(m.to_dict(), "Maintenance log updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@maintenance_bp.route("/<int:mid>", methods=["DELETE"])
@jwt_required()
@permission_required("maintenance:delete")
def delete_maintenance(mid):
    try:
        m = MaintenanceLog.query.get(mid)
        if not m:
            return error_response("Maintenance log not found", 404)
        db.session.delete(m)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="maintenance", action_type="DELETE", name=f"Task #{mid}")
        return success_response(message="Maintenance log deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ NETWORK LINKS ═══════════════════════════════

network_bp = Blueprint("network", __name__, url_prefix="/api/network-links")

@network_bp.route("", methods=["GET"])
@jwt_required()
def get_links():
    try:
        query = NetworkLink.query.order_by(NetworkLink.created_at.desc())
        items, total, page, per_page = paginate_query(query, default_per_page=50)
        return paginated_response([l.to_dict() for l in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@network_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("network:write")
def create_link():
    try:
        data = request.get_json()
        if not data or not data.get("source_device_id") or not data.get("target_device_id"):
            return error_response("source_device_id and target_device_id required", 400)
        if data["source_device_id"] == data["target_device_id"]:
            return error_response("Source and target device must be different", 400)
        link = NetworkLink(source_device_id=data["source_device_id"], target_device_id=data["target_device_id"],
                           link_type=data.get("link_type"), bandwidth=data.get("bandwidth"),
                           latency=data.get("latency"), packet_loss=data.get("packet_loss"),
                           status=data.get("status", "active"))
        db.session.add(link)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="network-links", action_type="CREATE", name=f"Link #{link.id} ({link.source_device_id} → {link.target_device_id})")
        return success_response(link.to_dict(), "Network link created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@network_bp.route("/<int:lid>", methods=["PUT"])
@jwt_required()
@permission_required("network:write")
def update_link(lid):
    try:
        link = NetworkLink.query.get(lid)
        if not link:
            return error_response("Network link not found", 404)
        data = request.get_json()
        for f in ["source_device_id","target_device_id","link_type","bandwidth","latency","packet_loss","status"]:
            if f in data:
                setattr(link, f, data[f])
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="network-links", action_type="UPDATE", name=f"Link #{link.id} ({link.source_device_id} → {link.target_device_id})")
        return success_response(link.to_dict(), "Network link updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@network_bp.route("/<int:lid>", methods=["DELETE"])
@jwt_required()
@permission_required("network:delete")
def delete_link(lid):
    try:
        link = NetworkLink.query.get(lid)
        if not link:
            return error_response("Network link not found", 404)
        db.session.delete(link)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="network-links", action_type="DELETE", name=f"Link #{lid}")
        return success_response(message="Network link deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ SLA POLICIES ═══════════════════════════════

sla_bp = Blueprint("sla", __name__, url_prefix="/api/sla-policies")

@sla_bp.route("", methods=["GET"])
@jwt_required()
def get_policies():
    try:
        policies = SLAPolicy.query.all()
        return success_response([p.to_dict() for p in policies])
    except Exception as e:
        return error_response(str(e))

# ═══════════════════════════════ AUDIT LOGS ═══════════════════════════════

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit-logs")

@audit_bp.route("", methods=["GET"])
@jwt_required()
@permission_required("audit:read")
def get_audit_logs():
    try:
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())
        resource = request.args.get("resource")
        action = request.args.get("action")
        if resource:
            query = query.filter(AuditLog.resource == resource)
        if action:
            query = query.filter(AuditLog.action == action)
        items, total, page, per_page = paginate_query(query)
        return paginated_response([a.to_dict() for a in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

# ═══════════════════════════════ INCIDENTS ═══════════════════════════════

incidents_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")

@incidents_bp.route("", methods=["GET"])
@jwt_required()
def get_incidents():
    try:
        query = Incident.query.filter_by(is_deleted=False).order_by(Incident.reported_at.desc())
        status = request.args.get("status")
        severity = request.args.get("severity")
        if status:
            query = query.filter(Incident.status == status)
        if severity:
            query = query.filter(Incident.severity == severity)
        items, total, page, per_page = paginate_query(query)
        return paginated_response([i.to_dict() for i in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@incidents_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("incidents:write")
def create_incident():
    try:
        data = request.get_json()
        if not data or not data.get("title"):
            return error_response("title is required", 400)
        inc = Incident(title=data["title"], description=data.get("description"),
                       severity=data.get("severity", "medium"), priority=data.get("priority", 3),
                       impact=data.get("impact"), affected_services=data.get("affected_services"),
                       reported_by_id=current_user_id())
        db.session.add(inc)
        db.session.flush()
        tl = IncidentTimeline(incident_id=inc.id, action="created", description="Incident created",
                              performed_by_id=current_user_id())
        db.session.add(tl)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="incidents", action_type="CREATE", name=inc.title)
        return success_response(inc.to_dict(), "Incident created", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@incidents_bp.route("/<int:iid>", methods=["GET"])
@jwt_required()
def get_incident(iid):
    try:
        inc = Incident.query.filter_by(id=iid, is_deleted=False).first()
        if not inc:
            return error_response("Incident not found", 404)
        data = inc.to_dict()
        data["timeline"] = [t.to_dict() for t in inc.timeline.order_by(IncidentTimeline.timestamp.asc()).all()]
        return success_response(data)
    except Exception as e:
        return error_response(str(e))

@incidents_bp.route("/<int:iid>", methods=["PUT"])
@jwt_required()
@permission_required("incidents:write")
def update_incident(iid):
    try:
        inc = Incident.query.filter_by(id=iid, is_deleted=False).first()
        if not inc:
            return error_response("Incident not found", 404)
        data = request.get_json()
        for f in ["title","description","severity","status","priority","impact",
                   "affected_services","root_cause","resolution_summary","lessons_learned"]:
            if f in data:
                setattr(inc, f, data[f])
        # Track status transitions
        if "status" in data:
            now = datetime.now(timezone.utc)
            if data["status"] == "acknowledged" and not inc.acknowledged_at:
                inc.acknowledged_at = now
            elif data["status"] == "resolved" and not inc.resolved_at:
                inc.resolved_at = now
            elif data["status"] == "closed" and not inc.closed_at:
                inc.closed_at = now
            tl = IncidentTimeline(incident_id=inc.id, action=f"status_changed_to_{data['status']}",
                                  description=f"Status changed to {data['status']}",
                                  performed_by_id=current_user_id())
            db.session.add(tl)
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="incidents", action_type="UPDATE", name=inc.title)
        return success_response(inc.to_dict(), "Incident updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

@incidents_bp.route("/<int:iid>", methods=["DELETE"])
@jwt_required()
@permission_required("incidents:delete")
def delete_incident(iid):
    try:
        inc = Incident.query.filter_by(id=iid, is_deleted=False).first()
        if not inc:
            return error_response("Incident not found", 404)
        inc.soft_delete()
        db.session.commit()
        from services.notification_service import notify_crud_action
        notify_crud_action(user_id=current_user_id(), resource_type="incidents", action_type="DELETE", name=inc.title)
        return success_response(message="Incident deleted")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))

# ═══════════════════════════════ NOTIFICATIONS ═══════════════════════════════

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    try:
        user_id = current_user_id()
        query = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc())
        unread_only = request.args.get("unread")
        if unread_only == "true":
            query = query.filter_by(is_read=False)
        items, total, page, per_page = paginate_query(query)
        return paginated_response([n.to_dict() for n in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))

@notifications_bp.route("/<int:nid>/read", methods=["PUT"])
@jwt_required()
def mark_read(nid):
    try:
        n = Notification.query.filter_by(id=nid, user_id=current_user_id()).first()
        if not n:
            return error_response("Notification not found", 404)
        n.is_read = True
        n.read_at = datetime.now(timezone.utc)
        db.session.commit()
        return success_response(message="Notification marked as read")
    except Exception as e:
        return error_response(str(e))

# ═══════════════════════════════ DROPDOWNS ═══════════════════════════════

dropdowns_bp = Blueprint("dropdowns", __name__, url_prefix="/api/dropdowns")

@dropdowns_bp.route("/locations", methods=["GET"])
@jwt_required()
def dropdown_locations():
    locs = Location.query.filter_by(is_deleted=False).order_by(Location.location_name).all()
    return success_response([{"id": l.id, "label": l.location_name, "city": l.city} for l in locs])

@dropdowns_bp.route("/technicians", methods=["GET"])
@jwt_required()
def dropdown_technicians():
    techs = Technician.query.filter_by(is_deleted=False).order_by(Technician.full_name).all()
    return success_response([{"id": t.id, "label": t.full_name, "status": t.status} for t in techs])

@dropdowns_bp.route("/vendors", methods=["GET"])
@jwt_required()
def dropdown_vendors():
    vendors = Vendor.query.filter_by(is_deleted=False).order_by(Vendor.vendor_name).all()
    return success_response([{"id": v.id, "label": v.vendor_name} for v in vendors])

@dropdowns_bp.route("/devices", methods=["GET"])
@jwt_required()
def dropdown_devices():
    devices = Device.query.filter_by(is_deleted=False).order_by(Device.device_name).all()
    return success_response([{"id": d.id, "label": f"{d.device_name} ({d.ip_address})"} for d in devices])

@dropdowns_bp.route("/sla-policies", methods=["GET"])
@jwt_required()
def dropdown_sla():
    policies = SLAPolicy.query.all()
    return success_response([{"id": p.id, "label": p.severity_level} for p in policies])

# ═══════════════════════════════ SEARCH ═══════════════════════════════

search_bp = Blueprint("search", __name__, url_prefix="/api/search")

@search_bp.route("", methods=["GET"])
@jwt_required()
def global_search():
    """Global search across devices, alerts, technicians, locations."""
    try:
        q = request.args.get("q", "").strip()
        if len(q) < 2:
            return error_response("Search query must be at least 2 characters", 400)

        results = {"devices": [], "alerts": [], "technicians": [], "locations": []}

        devices = Device.query.filter(Device.is_deleted == False, db.or_(
            Device.device_name.ilike(f"%{q}%"), Device.ip_address.ilike(f"%{q}%")
        )).limit(5).all()
        results["devices"] = [{"id": d.id, "name": d.device_name, "ip": d.ip_address, "status": d.status} for d in devices]

        alerts = Alert.query.filter(Alert.is_deleted == False, db.or_(
            Alert.alert_type.ilike(f"%{q}%"), Alert.message.ilike(f"%{q}%")
        )).limit(5).all()
        results["alerts"] = [{"id": a.id, "type": a.alert_type, "severity": a.severity, "status": a.status} for a in alerts]

        techs = Technician.query.filter(Technician.is_deleted == False,
            Technician.full_name.ilike(f"%{q}%")).limit(5).all()
        results["technicians"] = [{"id": t.id, "name": t.full_name, "status": t.status} for t in techs]

        locs = Location.query.filter(Location.is_deleted == False, db.or_(
            Location.location_name.ilike(f"%{q}%"), Location.city.ilike(f"%{q}%")
        )).limit(5).all()
        results["locations"] = [{"id": l.id, "name": l.location_name, "city": l.city} for l in locs]

        total = sum(len(v) for v in results.values())
        return success_response(results, f"Found {total} results")
    except Exception as e:
        return error_response(str(e))
