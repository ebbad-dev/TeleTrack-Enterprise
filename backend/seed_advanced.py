import os
from datetime import datetime, timezone, timedelta
from extensions import db
from models import (
    Technician, Location, Vendor, MaintenanceLog, SLAPolicy,
    AuditLog, Incident, Notification, Device, User, Alert
)

def seed_advanced(app):
    with app.app_context():
        from werkzeug.security import generate_password_hash
        # 1. Ensure at least one User exists
        from werkzeug.security import generate_password_hash
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            from models import Role
            admin_role = Role.query.filter_by(name='admin').first()
            admin_user = User(
                username="admin", 
                email="admin@teletrack.corp", 
                full_name="System Administrator",
                status="active"
            )
            if admin_role:
                admin_user.roles.append(admin_role)
            db.session.add(admin_user)
        
        admin_user.password_hash = generate_password_hash("admin123")
        db.session.commit()
        print("Admin user verified/updated with password: admin123")

        user_id = admin_user.id

        # 2. Locations
        if Location.query.count() < 4:
            locs = [
                Location(location_name="Alpha Datacenter", city="New York", country="USA", site_type="Primary", address_line="100 Wall St"),
                Location(location_name="Bravo Hub", city="London", country="UK", site_type="Secondary", address_line="45 Canary Wharf"),
                Location(location_name="Charlie Node", city="Tokyo", country="Japan", site_type="Edge", address_line="Shibuya 109"),
                Location(location_name="Delta Facility", city="Frankfurt", country="Germany", site_type="Backup", address_line="10 Euro Platz"),
            ]
            db.session.bulk_save_objects(locs)
            db.session.commit()
        
        loc_id = Location.query.first().id

        # 3. Vendors
        if Vendor.query.count() < 3:
            vendors = [
                Vendor(vendor_name="Cisco Systems", country_of_origin="USA", support_email="support@cisco.test", support_phone="1-800-553-2447", website="https://cisco.com"),
                Vendor(vendor_name="Juniper Networks", country_of_origin="USA", support_email="support@juniper.test", support_phone="1-888-314-5822", website="https://juniper.net"),
                Vendor(vendor_name="Arista", country_of_origin="USA", support_email="support@arista.test", website="https://arista.com"),
            ]
            db.session.bulk_save_objects(vendors)
            db.session.commit()

        # 4. Devices (Fleet)
        if Device.query.count() < 5:
            devices = [
                Device(device_name="NY-CORE-R01", device_type="Router", location_id=loc_id, status="online", ip_address="10.0.0.1", cpu_usage=45.2, memory_usage=62.1, temperature=42.5),
                Device(device_name="LON-BR-SW02", device_type="Switch", location_id=loc_id, status="online", ip_address="10.0.1.5", cpu_usage=12.5, memory_usage=34.8, temperature=38.2),
                Device(device_name="TOK-EDGE-F01", device_type="Firewall", location_id=loc_id, status="degraded", ip_address="10.0.2.10", cpu_usage=88.7, memory_usage=91.2, temperature=56.4),
                Device(device_name="FRA-SRV-H03", device_type="Server", location_id=loc_id, status="online", ip_address="10.0.3.15", cpu_usage=33.1, memory_usage=55.4, temperature=40.1),
                Device(device_name="NY-DIST-SW01", device_type="Switch", location_id=loc_id, status="offline", ip_address="10.0.0.2", cpu_usage=0, memory_usage=0, temperature=0),
            ]
            for d in devices:
                try:
                    db.session.add(d)
                    db.session.commit()
                except:
                    db.session.rollback()

        dev_id = Device.query.first().id

        # 5. Technicians
        if Technician.query.count() < 3:
            techs = [
                Technician(full_name="Sarah Jenkins", email="s.jenkins@teletrack.corp", specialization="Network Engineering", shift="Morning", status="available"),
                Technician(full_name="David Chen", email="d.chen@teletrack.corp", specialization="Hardware Replacement", shift="Evening", status="busy"),
                Technician(full_name="Marcus Vance", email="m.vance@teletrack.corp", specialization="Security", shift="Night", status="available"),
            ]
            for t in techs:
                try:
                    db.session.add(t)
                    db.session.commit()
                except:
                    db.session.rollback()
            
        tech_id = Technician.query.first().id

        # 6. SLA Policies
        if SLAPolicy.query.count() < 3:
            slas = [
                SLAPolicy(severity_level="critical", response_time_minutes=15, resolution_time_minutes=120),
                SLAPolicy(severity_level="high", response_time_minutes=30, resolution_time_minutes=240),
                SLAPolicy(severity_level="medium", response_time_minutes=120, resolution_time_minutes=1440),
            ]
            for s in slas:
                try:
                    db.session.add(s)
                    db.session.commit()
                except:
                    db.session.rollback()

        # 7. Alerts
        if Alert.query.count() < 10:
            alerts = [
                Alert(alert_type="Unauthorized Access", severity="critical", message="Multiple failed SSH attempts from 192.168.5.110", device_id=dev_id, status="open"),
                Alert(alert_type="High CPU Load", severity="high", message="CPU usage exceeded 90% threshold", device_id=dev_id, status="open"),
                Alert(alert_type="Link Flapping", severity="medium", message="Port GigabitEthernet0/1 changed state to down", device_id=dev_id, status="open"),
            ]
            for a in alerts:
                try:
                    db.session.add(a)
                    db.session.commit()
                except:
                    db.session.rollback()

        # 8. Incidents
        if Incident.query.count() < 5:
            incs = [
                Incident(title="Core Router Overload", description="NY-CORE-R01 experiencing high packet drop.", severity="critical", status="open", impact="Major", reported_by_id=user_id),
                Incident(title="Latency Spike", description="Link between NY and LON showing 200ms delay.", severity="high", status="open", impact="Moderate", reported_by_id=user_id),
            ]
            db.session.bulk_save_objects(incs)

        # 9. Device Metrics (TimeSeries)
        from models import DeviceMetric
        if DeviceMetric.query.count() < 50:
            import random
            for i in range(24):
                ts = datetime.now(timezone.utc) - timedelta(hours=i)
                m = DeviceMetric(device_id=dev_id, metric_type="cpu", value=random.uniform(20, 80), unit="%", timestamp=ts)
                db.session.add(m)
            db.session.commit()

        # 9. Network Links (Topology)
        from models.supporting import NetworkLink
        if NetworkLink.query.count() < 3:
            all_devs = Device.query.all()
            if len(all_devs) >= 2:
                links = [
                    NetworkLink(source_device_id=all_devs[0].id, target_device_id=all_devs[1].id, link_type="Fiber", status="active"),
                    NetworkLink(source_device_id=all_devs[1].id, target_device_id=all_devs[2].id, link_type="Ethernet", status="active"),
                ]
                db.session.bulk_save_objects(links)

        db.session.commit()
        print("Advanced seeding complete.")

if __name__ == "__main__":
    import app
    import random
    flask_app = app.create_app()
    seed_advanced(flask_app)
