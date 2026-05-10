"""
TeleTrack Enterprise — Device Models
Device management with status history tracking.
"""

from extensions import db
from models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class Device(TimestampMixin, SoftDeleteMixin, AuditMixin, db.Model):
    """Network device (router, switch, firewall, server, AP, etc.)."""

    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(150), nullable=False, index=True)
    device_type = db.Column(db.String(50))  # Router, Switch, Firewall, Server, AP
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=True)
    mac_address = db.Column(db.String(20), unique=True, nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    status = db.Column(
        db.String(30), default="online", nullable=False, index=True
    )  # online, offline, degraded, maintenance
    firmware_version = db.Column(db.String(100))
    installed_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    last_ping_time = db.Column(db.DateTime)
    uptime = db.Column(db.Float)  # hours
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    temperature = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    notes = db.Column(db.Text)

    # SNMP Configuration
    snmp_community = db.Column(db.String(100))
    snmp_version = db.Column(db.String(10), default="v2c")
    snmp_port = db.Column(db.Integer, default=161)
    monitoring_enabled = db.Column(db.Boolean, default=True)
    ping_interval = db.Column(db.Integer, default=60)  # seconds
    maintenance_until = db.Column(db.DateTime, nullable=True) # Silences alerts until this time

    # Relationships
    vendor = db.relationship("Vendor", backref="devices")
    location = db.relationship("Location", backref="devices")
    status_history = db.relationship(
        "DeviceStatusHistory",
        backref="device",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="DeviceStatusHistory.changed_at.desc()",
    )
    alerts = db.relationship(
        "Alert", backref="device", lazy="dynamic", cascade="all, delete-orphan"
    )
    maintenance_logs = db.relationship(
        "MaintenanceLog", backref="device", lazy="dynamic", cascade="all, delete-orphan"
    )
    metrics = db.relationship(
        "DeviceMetric", backref="device", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Device {self.device_name} ({self.ip_address})>"

    def to_dict(self):
        return {
            "id": self.id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "vendor_id": self.vendor_id,
            "vendor_name": self.vendor.vendor_name if self.vendor else None,
            "model": self.model,
            "serial_number": self.serial_number,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "location_id": self.location_id,
            "location_name": self.location.location_name if self.location else None,
            "status": self.status,
            "firmware_version": self.firmware_version,
            "installed_date": self.installed_date.isoformat() if self.installed_date else None,
            "warranty_expiry": self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            "last_ping_time": self.last_ping_time.isoformat() if self.last_ping_time else None,
            "uptime": self.uptime,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "temperature": self.temperature,
            "image_url": self.image_url,
            "monitoring_enabled": self.monitoring_enabled,
            "maintenance_until": self.maintenance_until.isoformat() if self.maintenance_until else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DeviceStatusHistory(db.Model):
    """Audit trail for device status transitions."""

    __tablename__ = "device_status_history"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    previous_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    reason = db.Column(db.String(500))
    changed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    changed_at = db.Column(
        db.DateTime,
        default=db.func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    changed_by = db.relationship("User", foreign_keys=[changed_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "reason": self.reason,
            "changed_by": self.changed_by.full_name if self.changed_by else None,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
        }


class DeviceMetric(db.Model):
    """Time-series metrics for device monitoring."""

    __tablename__ = "device_metrics"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    metric_type = db.Column(
        db.String(50), nullable=False, index=True
    )  # cpu, memory, temperature, latency, interface_in, interface_out
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))  # %, °C, ms, Mbps
    timestamp = db.Column(
        db.DateTime,
        default=db.func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        db.Index("idx_metric_device_type_time", "device_id", "metric_type", "timestamp"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "metric_type": self.metric_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
