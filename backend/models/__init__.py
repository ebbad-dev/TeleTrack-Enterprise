"""
TeleTrack Enterprise — Models Package
Imports all models so SQLAlchemy discovers them for migrations.
"""

# Mixins (imported by other models)
from models.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin

# Core Models
from models.user import (
    User,
    Role,
    Permission,
    UserSession,
    APIKey,
    LoginHistory,
    user_roles,
    role_permissions,
)
from models.device import Device, DeviceStatusHistory, DeviceMetric
from models.alert import Alert, AlertComment
from models.incident import Incident, IncidentTimeline, Escalation

# Supporting Models
from models.supporting import (
    Location,
    Vendor,
    Technician,
    SLAPolicy,
    MaintenanceLog,
    NetworkLink,
    AuditLog,
    Notification,
    FileAttachment,
    Department,
    Team,
)

__all__ = [
    # Mixins
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    # User & Auth
    "User",
    "Role",
    "Permission",
    "UserSession",
    "APIKey",
    "LoginHistory",
    "user_roles",
    "role_permissions",
    # Devices
    "Device",
    "DeviceStatusHistory",
    "DeviceMetric",
    # Alerts
    "Alert",
    "AlertComment",
    # Incidents
    "Incident",
    "IncidentTimeline",
    "Escalation",
    # Supporting
    "Location",
    "Vendor",
    "Technician",
    "SLAPolicy",
    "MaintenanceLog",
    "NetworkLink",
    "AuditLog",
    "Notification",
    "FileAttachment",
    "Department",
    "Team",
]
