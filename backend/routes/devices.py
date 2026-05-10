"""
TeleTrack Enterprise — Device Routes
Full CRUD for device management with filtering, status updates, and history.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from extensions import db
from models import Device, DeviceStatusHistory, DeviceMetric, AuditLog
from utils.response import success_response, error_response, paginated_response
from utils.validators import validate_ip_address, validate_mac_address
from utils.pagination import paginate_query
from auth.decorators import permission_required
from auth.utils import current_user_id

devices_bp = Blueprint("devices", __name__, url_prefix="/api/devices")


@devices_bp.route("", methods=["GET"])
@jwt_required()
def get_devices():
    """Get all devices with optional filtering and pagination."""
    try:
        query = Device.query.filter_by(is_deleted=False)

        # Filters
        status = request.args.get("status")
        device_type = request.args.get("device_type")
        location_id = request.args.get("location_id", type=int)
        vendor_id = request.args.get("vendor_id", type=int)
        search = request.args.get("search", "").strip()

        if status:
            query = query.filter(Device.status == status)
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if location_id:
            query = query.filter(Device.location_id == location_id)
        if vendor_id:
            query = query.filter(Device.vendor_id == vendor_id)
        if search:
            query = query.filter(
                db.or_(
                    Device.device_name.ilike(f"%{search}%"),
                    Device.ip_address.ilike(f"%{search}%"),
                    Device.mac_address.ilike(f"%{search}%"),
                    Device.model.ilike(f"%{search}%"),
                )
            )

        # Sort
        sort_by = request.args.get("sort_by", "device_name")
        sort_order = request.args.get("sort_order", "asc")
        if hasattr(Device, sort_by):
            col = getattr(Device, sort_by)
            query = query.order_by(col.desc() if sort_order == "desc" else col.asc())
        else:
            query = query.order_by(Device.device_name.asc())

        items, total, page, per_page = paginate_query(query)
        return paginated_response([d.to_dict() for d in items], total, page, per_page)
    except Exception as e:
        return error_response(str(e))


@devices_bp.route("/<int:device_id>", methods=["GET"])
@jwt_required()
def get_device(device_id):
    """Get detailed info for a specific device."""
    try:
        device = Device.query.filter_by(id=device_id, is_deleted=False).first()
        if not device:
            return error_response("Device not found", 404)

        data = device.to_dict()

        # Include recent status history
        history = (
            DeviceStatusHistory.query.filter_by(device_id=device_id)
            .order_by(DeviceStatusHistory.changed_at.desc())
            .limit(20)
            .all()
        )
        data["status_history"] = [h.to_dict() for h in history]

        # Include recent alerts
        from models import Alert
        alerts = (
            Alert.query.filter_by(device_id=device_id, is_deleted=False)
            .order_by(Alert.alert_time.desc())
            .limit(10)
            .all()
        )
        data["recent_alerts"] = [a.to_dict() for a in alerts]

        return success_response(data)
    except Exception as e:
        return error_response(str(e))


@devices_bp.route("", methods=["POST"])
@jwt_required()
@permission_required("devices:write")
def create_device():
    """Create a new device with validation."""
    try:
        data = request.get_json()
        if not data:
            return error_response("Request body required", 400)

        # Validate required fields
        required = ["device_name", "location_id"]
        for field in required:
            if not data.get(field):
                return error_response(f"Missing required field: {field}", 400)

        # Validate IP
        if data.get("ip_address") and not validate_ip_address(data["ip_address"]):
            return error_response("Invalid IP address format", 400)

        # Check IP uniqueness
        if data.get("ip_address"):
            existing = Device.query.filter_by(ip_address=data["ip_address"], is_deleted=False).first()
            if existing:
                return error_response("IP address already in use", 409)

        # Validate MAC
        if data.get("mac_address") and not validate_mac_address(data["mac_address"]):
            return error_response("Invalid MAC address format", 400)

        device = Device(
            device_name=data["device_name"],
            device_type=data.get("device_type"),
            vendor_id=data.get("vendor_id"),
            model=data.get("model"),
            serial_number=data.get("serial_number"),
            ip_address=data.get("ip_address"),
            mac_address=data.get("mac_address"),
            location_id=data["location_id"],
            status=data.get("status", "online"),
            firmware_version=data.get("firmware_version"),
            installed_date=data.get("installed_date"),
            image_url=data.get("image_url"),
            notes=data.get("notes"),
            snmp_community=data.get("snmp_community"),
            monitoring_enabled=data.get("monitoring_enabled", True),
            created_by_id=current_user_id(),
        )

        db.session.add(device)
        db.session.commit()

        # Audit log
        audit = AuditLog(
            user_id=current_user_id(),
            action="CREATE",
            resource="devices",
            resource_id=device.id,
            new_value=f"Device '{device.device_name}' created",
            ip_address=request.remote_addr,
        )
        db.session.add(audit)
        db.session.commit()

        return success_response(device.to_dict(), "Device created successfully", 201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@devices_bp.route("/<int:device_id>", methods=["PUT"])
@jwt_required()
@permission_required("devices:write")
def update_device(device_id):
    """Update device information."""
    try:
        device = Device.query.filter_by(id=device_id, is_deleted=False).first()
        if not device:
            return error_response("Device not found", 404)

        data = request.get_json()
        if not data:
            return error_response("Request body required", 400)

        # Update allowed fields
        allowed = [
            "device_name", "device_type", "vendor_id", "model", "serial_number",
            "firmware_version", "image_url", "notes", "snmp_community",
            "snmp_version", "snmp_port", "monitoring_enabled", "ping_interval",
        ]
        for field in allowed:
            if field in data:
                setattr(device, field, data[field])

        device.updated_by_id = current_user_id()
        db.session.commit()

        # Audit log
        audit = AuditLog(
            user_id=current_user_id(),
            action="UPDATE",
            resource="devices",
            resource_id=device.id,
            new_value=f"Device '{device.device_name}' updated",
            ip_address=request.remote_addr,
        )
        db.session.add(audit)
        db.session.commit()

        return success_response(device.to_dict(), "Device updated successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@devices_bp.route("/<int:device_id>/status", methods=["PUT"])
@jwt_required()
@permission_required("devices:write")
def update_device_status(device_id):
    """Update device status with history tracking."""
    try:
        device = Device.query.filter_by(id=device_id, is_deleted=False).first()
        if not device:
            return error_response("Device not found", 404)

        data = request.get_json()
        new_status = data.get("status")
        reason = data.get("reason", "Status update")

        if not new_status:
            return error_response("Status is required", 400)

        old_status = device.status

        # Create history record
        history = DeviceStatusHistory(
            device_id=device.id,
            previous_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by_id=current_user_id(),
        )
        db.session.add(history)

        # Update device
        device.status = new_status
        device.updated_by_id = current_user_id()

        # Auto-create alert if device goes offline
        if new_status == "offline" and old_status != "offline":
            from models import Alert
            alert = Alert(
                device_id=device.id,
                alert_type="Device Offline",
                severity="high",
                message=f"Device '{device.device_name}' went offline: {reason}",
                status="open",
                created_by_id=current_user_id(),
            )
            db.session.add(alert)

        db.session.commit()

        return success_response(device.to_dict(), "Device status updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@devices_bp.route("/<int:device_id>", methods=["DELETE"])
@jwt_required()
@permission_required("devices:delete")
def delete_device(device_id):
    """Soft-delete a device."""
    try:
        device = Device.query.filter_by(id=device_id, is_deleted=False).first()
        if not device:
            return error_response("Device not found", 404)

        device.soft_delete()

        # Audit log
        audit = AuditLog(
            user_id=current_user_id(),
            action="DELETE",
            resource="devices",
            resource_id=device.id,
            old_value=f"Device '{device.device_name}' soft-deleted",
            ip_address=request.remote_addr,
        )
        db.session.add(audit)
        db.session.commit()

        return success_response(message="Device deleted successfully")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@devices_bp.route("/<int:device_id>/metrics", methods=["GET"])
@jwt_required()
def get_device_metrics(device_id):
    """Get historical metrics for a device."""
    try:
        device = Device.query.filter_by(id=device_id, is_deleted=False).first()
        if not device:
            return error_response("Device not found", 404)

        metric_type = request.args.get("type")  # cpu, memory, temperature, latency
        hours = int(request.args.get("hours", 24))

        from datetime import timedelta
        since = db.func.now() - timedelta(hours=hours)

        query = DeviceMetric.query.filter(
            DeviceMetric.device_id == device_id,
            DeviceMetric.timestamp >= since,
        )

        if metric_type:
            query = query.filter(DeviceMetric.metric_type == metric_type)

        metrics = query.order_by(DeviceMetric.timestamp.asc()).limit(500).all()

        return success_response([m.to_dict() for m in metrics])
    except Exception as e:
        return error_response(str(e))


@devices_bp.route("/discover", methods=["POST"])
@jwt_required()
@permission_required("devices:write")
def discover_network():
    """Trigger an automated subnet ping scan to discover devices."""
    data = request.get_json()
    if not data or "subnet" not in data:
        from utils.response import error_response
        return error_response("Subnet (CIDR format) is required", 400)

    subnet = data["subnet"]
    
    # Trigger Celery task asynchronously
    from tasks.discovery import scan_subnet
    task = scan_subnet.delay(subnet, default_type=data.get("default_type", "Server"))
    
    from utils.response import success_response
    return success_response({
        "message": f"Network discovery initiated for {subnet}", 
        "task_id": task.id
    })
