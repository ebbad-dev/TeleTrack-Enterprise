"""
TeleTrack Enterprise — SLA Breach Checker Task
Periodic Celery task that checks for SLA deadline breaches.
"""

from celery import shared_task
from datetime import datetime, timezone
from extensions import db
from models import Alert, Incident
import logging

logger = logging.getLogger(__name__)


@shared_task(name='tasks.notifications.check_sla_breaches')
def check_sla_breaches():
    """
    Check all open alerts and incidents for SLA deadline breaches.
    Marks them as breached and generates notifications.
    """
    logger.info("Running SLA breach check...")
    now = datetime.now(timezone.utc)
    breached_count = 0

    # Check alerts with SLA deadlines
    alerts = Alert.query.filter(
        Alert.status.in_(["open", "assigned", "in_progress"]),
        Alert.is_deleted == False,
        Alert.sla_breached == False,
    ).all()

    for alert in alerts:
        breached = False

        if alert.sla_response_deadline and now > alert.sla_response_deadline:
            if not alert.acknowledged_at:
                breached = True

        if alert.sla_resolution_deadline and now > alert.sla_resolution_deadline:
            if not alert.resolved_time:
                breached = True

        if breached:
            alert.sla_breached = True
            breached_count += 1

            try:
                from services.notification_service import notify_sla_breach
                notify_sla_breach(alert)
            except Exception as e:
                logger.error(f"Failed to send SLA breach notification for alert {alert.id}: {e}")

    # Check incidents with SLA deadlines
    incidents = Incident.query.filter(
        Incident.status.in_(["open", "acknowledged", "investigating"]),
        Incident.is_deleted == False,
        Incident.sla_breached == False,
    ).all()

    for incident in incidents:
        breached = False

        if incident.sla_response_deadline and now > incident.sla_response_deadline:
            if not incident.acknowledged_at:
                breached = True

        if incident.sla_resolution_deadline and now > incident.sla_resolution_deadline:
            if not incident.resolved_at:
                breached = True

        if breached:
            incident.sla_breached = True
            breached_count += 1

    db.session.commit()
    logger.info(f"SLA breach check completed. {breached_count} new breaches found.")
    return f"{breached_count} breaches"
