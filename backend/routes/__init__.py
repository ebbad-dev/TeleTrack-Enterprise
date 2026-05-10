"""
TeleTrack Enterprise — Routes Package
Register all blueprints with the Flask app.
"""

from routes.dashboard import dashboard_bp
from routes.devices import devices_bp
from routes.alerts import alerts_bp
from routes.export import export_bp
from routes.crud import (
    technicians_bp, locations_bp, vendors_bp, maintenance_bp,
    network_bp, sla_bp, audit_bp, incidents_bp, notifications_bp,
    dropdowns_bp, search_bp,
)


def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    blueprints = [
        dashboard_bp,
        devices_bp,
        alerts_bp,
        export_bp,
        technicians_bp,
        locations_bp,
        vendors_bp,
        maintenance_bp,
        network_bp,
        sla_bp,
        audit_bp,
        incidents_bp,
        notifications_bp,
        dropdowns_bp,
        search_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)
