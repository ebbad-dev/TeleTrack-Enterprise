"""
TeleTrack Enterprise — Blueprint Registration
Registers all route blueprints with the Flask application.
"""


def register_routes(app):
    """Register all API blueprints."""

    # Auth
    from auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    # Dashboard
    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Devices
    from routes.devices import devices_bp
    app.register_blueprint(devices_bp)

    # Alerts
    from routes.alerts import alerts_bp
    app.register_blueprint(alerts_bp)

    # Files
    from routes.files import files_bp
    app.register_blueprint(files_bp)

    # Export
    from routes.export import export_bp
    app.register_blueprint(export_bp)

    # CRUD Blueprints (Technicians, Locations, Vendors, Maintenance,
    # Network Links, SLA, Audit, Incidents, Notifications, Dropdowns, Search)
    from routes.crud import (
        technicians_bp, locations_bp, vendors_bp, maintenance_bp,
        network_bp, sla_bp, audit_bp, incidents_bp, notifications_bp,
        dropdowns_bp, search_bp,
    )
    app.register_blueprint(technicians_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(sla_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(dropdowns_bp)
    app.register_blueprint(search_bp)

    from routes.database_objects import db_objects_bp
    app.register_blueprint(db_objects_bp)
