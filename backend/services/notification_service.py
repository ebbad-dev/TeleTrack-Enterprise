"""
TeleTrack Enterprise — Notification Service
Generates in-app notifications on key system events.
Emits WebSocket events for real-time delivery.
"""

import logging
from extensions import db, socketio
from models import Notification

logger = logging.getLogger(__name__)


def create_notification(user_id, title, message, notification_type="info", channel="in_app", link=None):
    """
    Create an in-app notification and push it via WebSocket.
    """
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel,
            link=link,
        )
        db.session.add(notif)
        db.session.flush()

        # Emit via WebSocket for real-time delivery
        socketio.emit("new_notification", notif.to_dict(), room=f"user_{user_id}")
        return notif
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        return None


def notify_device_offline(device):
    """Notify admins when a device goes offline."""
    from models import User, Role
    admin_roles = Role.query.filter(Role.name.in_(["super_admin", "network_admin", "noc_operator"])).all()
    admin_ids = set()
    for role in admin_roles:
        for user in role.users:
            if user.is_active:
                admin_ids.add(user.id)

    for uid in admin_ids:
        create_notification(
            user_id=uid,
            title="Device Offline",
            message=f"🔴 {device.device_name} ({device.ip_address}) went OFFLINE",
            notification_type="error",
            link=f"/devices",
        )


def notify_device_online(device):
    """Notify admins when a device comes back online."""
    from models import User, Role
    admin_roles = Role.query.filter(Role.name.in_(["super_admin", "network_admin"])).all()
    admin_ids = set()
    for role in admin_roles:
        for user in role.users:
            if user.is_active:
                admin_ids.add(user.id)

    for uid in admin_ids:
        create_notification(
            user_id=uid,
            title="Device Recovered",
            message=f"🟢 {device.device_name} ({device.ip_address}) is back ONLINE",
            notification_type="success",
            link=f"/devices",
        )


def notify_new_alert(alert):
    """Notify admins when a new critical/high alert is generated."""
    if alert.severity not in ("critical", "high"):
        return

    from models import Role
    admin_roles = Role.query.filter(Role.name.in_(["super_admin", "network_admin", "noc_operator"])).all()
    admin_ids = set()
    for role in admin_roles:
        for user in role.users:
            if user.is_active:
                admin_ids.add(user.id)

    severity_emoji = "🚨" if alert.severity == "critical" else "⚠️"
    for uid in admin_ids:
        create_notification(
            user_id=uid,
            title=f"{alert.severity.upper()} Alert",
            message=f"{severity_emoji} {alert.alert_type}: {alert.message[:100]}",
            notification_type="warning" if alert.severity == "high" else "error",
            link=f"/alerts",
        )


def notify_sla_breach(alert):
    """Notify admins when an SLA is breached."""
    from models import Role
    admin_roles = Role.query.filter(Role.name.in_(["super_admin", "network_admin", "it_manager"])).all()
    admin_ids = set()
    for role in admin_roles:
        for user in role.users:
            if user.is_active:
                admin_ids.add(user.id)

    for uid in admin_ids:
        create_notification(
            user_id=uid,
            title="SLA Breach",
            message=f"⏰ SLA breached on Alert #{alert.id}: {alert.alert_type}",
            notification_type="error",
            link=f"/alerts",
        )


def notify_incident_created(incident):
    """Notify admins when a new incident is created."""
    from models import Role
    admin_roles = Role.query.filter(Role.name.in_(["super_admin", "network_admin", "noc_operator"])).all()
    admin_ids = set()
    for role in admin_roles:
        for user in role.users:
            if user.is_active:
                admin_ids.add(user.id)

    for uid in admin_ids:
        create_notification(
            user_id=uid,
            title="New Incident",
            message=f"🔥 [{incident.severity.upper()}] {incident.title}",
            notification_type="warning",
            link=f"/incidents",
        )


def notify_crud_action(user_id, resource_type, action_type, name):
    """
    Create an in-app notification when a CRUD action (CREATE, UPDATE, DELETE) is performed.
    """
    action_verbs = {
        "CREATE": "created",
        "UPDATE": "updated",
        "DELETE": "deleted"
    }
    verb = action_verbs.get(action_type.upper(), "modified")
    
    emoji = "➕" if action_type.upper() == "CREATE" else "✏️" if action_type.upper() == "UPDATE" else "🗑️"
    
    title = f"{resource_type.title()} {action_type.title()}d"
    message = f"{emoji} Record '{name}' in {resource_type} table was successfully {verb}."
    
    create_notification(
        user_id=user_id or 1,
        title=title,
        message=message,
        notification_type="success" if action_type.upper() != "DELETE" else "warning",
        link=f"/{resource_type}"
    )
