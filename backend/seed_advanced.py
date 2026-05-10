import os
from datetime import datetime, timezone, timedelta
from extensions import db
from models import (
    Technician, Location, Vendor, MaintenanceLog, SLAPolicy,
    AuditLog, Incident, Notification, Device, User
)

def seed_advanced(app):
    with app.app_context():
        # Check if we already have technicians
        if Technician.query.count() < 5:
            techs = [
                Technician(full_name="Sarah Jenkins", email="s.jenkins@teletrack.corp", specialization="Network Engineering", shift="Morning", status="available"),
                Technician(full_name="David Chen", email="d.chen@teletrack.corp", specialization="Hardware Replacement", shift="Evening", status="busy"),
                Technician(full_name="Marcus Vance", email="m.vance@teletrack.corp", specialization="Security", shift="Night", status="available"),
                Technician(full_name="Elena Rostova", email="e.rostova@teletrack.corp", specialization="Fiber Optics", shift="Morning", status="available"),
                Technician(full_name="James Taggart", email="j.taggart@teletrack.corp", specialization="Datacenter Ops", shift="Flexible", status="busy"),
            ]
            db.session.bulk_save_objects(techs)
            
        if Location.query.count() < 4:
            locs = [
                Location(location_name="Alpha Datacenter", city="New York", country="USA", site_type="Primary", address_line="100 Wall St"),
                Location(location_name="Bravo Hub", city="London", country="UK", site_type="Secondary", address_line="45 Canary Wharf"),
                Location(location_name="Charlie Node", city="Tokyo", country="Japan", site_type="Edge", address_line="Shibuya 109"),
                Location(location_name="Delta Facility", city="Frankfurt", country="Germany", site_type="Backup", address_line="10 Euro Platz"),
            ]
            db.session.bulk_save_objects(locs)

        if Vendor.query.count() < 3:
            vendors = [
                Vendor(vendor_name="Cisco Systems", country_of_origin="USA", support_email="support@cisco.test", support_phone="1-800-553-2447", website="https://cisco.com"),
                Vendor(vendor_name="Juniper Networks", country_of_origin="USA", support_email="support@juniper.test", support_phone="1-888-314-5822", website="https://juniper.net"),
                Vendor(vendor_name="Arista", country_of_origin="USA", support_email="support@arista.test", website="https://arista.com"),
            ]
            db.session.bulk_save_objects(vendors)
            
        if SLAPolicy.query.count() < 3:
            slas = [
                SLAPolicy(severity_level="critical", max_response_time_minutes=15, max_resolution_time_minutes=120),
                SLAPolicy(severity_level="high", max_response_time_minutes=30, max_resolution_time_minutes=240),
                SLAPolicy(severity_level="medium", max_response_time_minutes=120, max_resolution_time_minutes=1440),
            ]
            db.session.bulk_save_objects(slas)

        db.session.commit()
        
        # We need IDs for foreign keys
        tech_id = Technician.query.first().id
        dev_id = Device.query.first().id
        user_id = User.query.first().id
        
        if MaintenanceLog.query.count() < 3:
            logs = [
                MaintenanceLog(device_id=dev_id, technician_id=tech_id, maintenance_type="Preventive", description="Routine firmware upgrade and dusting.", outcome="Successful", scheduled_date=datetime.now(timezone.utc) - timedelta(days=5)),
                MaintenanceLog(device_id=dev_id, technician_id=tech_id, maintenance_type="Corrective", description="Replaced failing power supply.", outcome="Successful", scheduled_date=datetime.now(timezone.utc) - timedelta(days=2)),
            ]
            db.session.bulk_save_objects(logs)

        if Incident.query.count() < 3:
            incs = [
                Incident(title="Core Router Failure", description="London Bravo Hub core router stopped responding to BGP.", severity="critical", status="resolved", impact="Major", reported_by_id=user_id),
                Incident(title="High Latency on Trans-Atlantic", description="Fiber cut caused routing fallback resulting in +40ms latency.", severity="high", status="open", impact="Moderate", reported_by_id=user_id),
            ]
            db.session.bulk_save_objects(incs)
            
        if AuditLog.query.count() < 10:
            audits = [
                AuditLog(user_id=user_id, action="LOGIN", resource="System", ip_address="192.168.1.50"),
                AuditLog(user_id=user_id, action="CREATE", resource="Device", ip_address="192.168.1.50"),
                AuditLog(user_id=user_id, action="UPDATE", resource="Alert", ip_address="192.168.1.50"),
            ]
            db.session.bulk_save_objects(audits)

        db.session.commit()
        print("Advanced seeding complete.")

if __name__ == "__main__":
    import app
    # Create mock app context
    flask_app = app.create_app()
    seed_advanced(flask_app)
