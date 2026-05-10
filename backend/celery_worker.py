"""
TeleTrack Enterprise — Celery Worker Configuration
Background task runner with periodic beat schedule.
"""

import os
import sys
from celery import Celery
from celery.schedules import crontab

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create Flask app context for Celery tasks
flask_app = create_app()


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(flask_app)

# ═══════════════════════════════════════════════════════════════════
# Beat Schedule — Periodic Tasks
# ═══════════════════════════════════════════════════════════════════

celery.conf.beat_schedule = {
    # Ping all devices every 60 seconds
    'ping-devices-every-minute': {
        'task': 'tasks.monitoring.ping_all_devices',
        'schedule': 60.0,
    },
    # Collect device metrics every 5 minutes
    'collect-metrics-every-5-minutes': {
        'task': 'tasks.monitoring.collect_device_metrics',
        'schedule': 300.0,
    },
    # Check SLA breaches every 2 minutes
    'check-sla-breaches-every-2-minutes': {
        'task': 'tasks.notifications.check_sla_breaches',
        'schedule': 120.0,
    },
    # AI Predictive Analytics every 10 minutes
    'analyze-predictive-trends': {
        'task': 'tasks.monitoring.analyze_predictive_trends',
        'schedule': 600.0,
    },
}
celery.conf.timezone = 'UTC'

# Import task modules so Celery discovers them
import tasks.monitoring
import tasks.notifications
