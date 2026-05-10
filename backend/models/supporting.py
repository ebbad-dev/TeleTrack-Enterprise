"""
TeleTrack Enterprise — Supporting Models
Location, Vendor, Technician, SLA, Maintenance, Network, Audit, Notification, Organization.
"""

from extensions import db
from models.mixins import TimestampMixin, SoftDeleteMixin


# ═══════════════════════════════════════════════════════════════════
# Location
# ═══════════════════════════════════════════════════════════════════


class Location(TimestampMixin, SoftDeleteMixin, db.Model):
    """Physical site or data center location."""

    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    site_type = db.Column(db.String(50))  # Headquarters, Data Center, Branch, Hub, Node
    address_line = db.Column(db.String(250))
    contact_person = db.Column(db.String(150))
    contact_phone = db.Column(db.String(30))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    image_url = db.Column(db.String(500))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Location {self.location_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "location_name": self.location_name,
            "city": self.city,
            "country": self.country,
            "site_type": self.site_type,
            "address_line": self.address_line,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "image_url": self.image_url,
            "device_count": self.devices.count() if hasattr(self, "devices") else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Vendor
# ═══════════════════════════════════════════════════════════════════


class Vendor(TimestampMixin, SoftDeleteMixin, db.Model):
    """Device manufacturer / vendor."""

    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(150), unique=True, nullable=False)
    country_of_origin = db.Column(db.String(100))
    support_email = db.Column(db.String(150))
    support_phone = db.Column(db.String(30))
    website = db.Column(db.String(255))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Vendor {self.vendor_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_name": self.vendor_name,
            "country_of_origin": self.country_of_origin,
            "support_email": self.support_email,
            "support_phone": self.support_phone,
            "website": self.website,
            "device_count": len(self.devices) if self.devices else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Technician
# ═══════════════════════════════════════════════════════════════════


class Technician(TimestampMixin, SoftDeleteMixin, db.Model):
    """Field technician for alert assignment and maintenance."""

    __tablename__ = "technicians"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    specialization = db.Column(db.String(100))
    shift = db.Column(db.String(30))  # Morning, Evening, Night, Flexible
    status = db.Column(
        db.String(30), default="available", nullable=False, index=True
    )  # available, busy, on_leave, inactive
    total_alerts = db.Column(db.Integer, default=0)
    resolved_alerts = db.Column(db.Integer, default=0)
    average_resolution_time = db.Column(db.Integer)  # minutes
    image_url = db.Column(db.String(500))

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="technician_profile")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Technician {self.full_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "specialization": self.specialization,
            "shift": self.shift,
            "status": self.status,
            "total_alerts": self.total_alerts,
            "resolved_alerts": self.resolved_alerts,
            "average_resolution_time": self.average_resolution_time,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# SLA Policy
# ═══════════════════════════════════════════════════════════════════


class SLAPolicy(TimestampMixin, db.Model):
    """Service Level Agreement definitions per severity."""

    __tablename__ = "sla_policies"

    id = db.Column(db.Integer, primary_key=True)
    severity_level = db.Column(db.String(30), unique=True, nullable=False)
    response_time_minutes = db.Column(db.Integer, nullable=False)
    resolution_time_minutes = db.Column(db.Integer, nullable=False)
    escalation_required = db.Column(db.Boolean, default=False)
    notification_interval = db.Column(db.Integer, default=30)  # minutes between reminders

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<SLAPolicy {self.severity_level}>"

    def to_dict(self):
        return {
            "id": self.id,
            "severity_level": self.severity_level,
            "response_time_minutes": self.response_time_minutes,
            "resolution_time_minutes": self.resolution_time_minutes,
            "escalation_required": self.escalation_required,
            "notification_interval": self.notification_interval,
        }


# ═══════════════════════════════════════════════════════════════════
# Maintenance Log
# ═══════════════════════════════════════════════════════════════════


class MaintenanceLog(TimestampMixin, db.Model):
    """Device maintenance activity records."""

    __tablename__ = "maintenance_logs"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    technician_id = db.Column(
        db.Integer, db.ForeignKey("technicians.id"), nullable=True
    )
    maintenance_type = db.Column(
        db.String(100), nullable=False
    )  # Preventive, Corrective, Emergency, Upgrade
    description = db.Column(db.String(500))
    scheduled_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    outcome = db.Column(db.String(50))  # Success, Partial, Failed, Rescheduled
    notes = db.Column(db.Text)
    image_url = db.Column(db.String(500))

    # Relationships
    technician = db.relationship("Technician", foreign_keys=[technician_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device.device_name if self.device else None,
            "technician_id": self.technician_id,
            "technician_name": self.technician.full_name if self.technician else None,
            "maintenance_type": self.maintenance_type,
            "description": self.description,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "duration_minutes": self.duration_minutes,
            "outcome": self.outcome,
            "notes": self.notes,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Network Link
# ═══════════════════════════════════════════════════════════════════


class NetworkLink(TimestampMixin, db.Model):
    """Network connection between two devices."""

    __tablename__ = "network_links"

    id = db.Column(db.Integer, primary_key=True)
    source_device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    target_device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    link_type = db.Column(db.String(50))  # Fiber, Ethernet, VPN, MPLS, Wireless
    bandwidth = db.Column(db.String(50))
    latency = db.Column(db.String(50))
    packet_loss = db.Column(db.String(50))
    status = db.Column(db.String(30), default="active")  # active, degraded, down

    # Relationships
    source_device = db.relationship("Device", foreign_keys=[source_device_id])
    target_device = db.relationship("Device", foreign_keys=[target_device_id])

    __table_args__ = (
        db.CheckConstraint("source_device_id != target_device_id", name="ck_link_different"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "source_device_id": self.source_device_id,
            "source_device_name": self.source_device.device_name if self.source_device else None,
            "target_device_id": self.target_device_id,
            "target_device_name": self.target_device.device_name if self.target_device else None,
            "link_type": self.link_type,
            "bandwidth": self.bandwidth,
            "latency": self.latency,
            "packet_loss": self.packet_loss,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Audit Log
# ═══════════════════════════════════════════════════════════════════


class AuditLog(db.Model):
    """System-wide activity audit trail."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource = db.Column(db.String(100), nullable=False, index=True)
    resource_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(
        db.DateTime, default=db.func.now(), nullable=False, index=True
    )

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user.full_name if self.user else "System",
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Notification
# ═══════════════════════════════════════════════════════════════════


class Notification(db.Model):
    """In-app and multi-channel notifications."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(
        db.String(50), default="info"
    )  # info, warning, error, success, alert
    channel = db.Column(db.String(30), default="in_app")  # in_app, email, sms, push
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    link = db.Column(db.String(500))  # deep link to related resource
    created_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False, index=True
    )

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="notifications")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "channel": self.channel,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "link": self.link,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# File Attachment
# ═══════════════════════════════════════════════════════════════════


class FileAttachment(TimestampMixin, db.Model):
    """File evidence (screenshots, configs) attached to incidents."""

    __tablename__ = "file_attachments"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # bytes
    mimetype = db.Column(db.String(100), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    uploader = db.relationship("User", foreign_keys=[uploaded_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mimetype": self.mimetype,
            "uploaded_by": self.uploader.full_name if self.uploader else "System",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ═══════════════════════════════════════════════════════════════════
# Organization Models (Department, Team)
# ═══════════════════════════════════════════════════════════════════


class Department(TimestampMixin, db.Model):
    """Organization department."""

    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    head_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    head = db.relationship("User", foreign_keys=[head_user_id])
    teams = db.relationship("Team", backref="department", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "head": self.head.full_name if self.head else None,
        }


class Team(TimestampMixin, db.Model):
    """Team within a department."""

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(
        db.Integer, db.ForeignKey("departments.id"), nullable=True
    )
    lead_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    lead = db.relationship("User", foreign_keys=[lead_user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department.name if self.department else None,
            "lead": self.lead.full_name if self.lead else None,
        }
