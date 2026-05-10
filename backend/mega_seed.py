import os
import random
from datetime import datetime, timezone, timedelta
from extensions import db
from models import (
    Technician, Location, Vendor, MaintenanceLog, SLAPolicy,
    AuditLog, Incident, Notification, Device, User, Alert,
    DeviceMetric, Department, Team, Permission, Role
)
from auth.utils import hash_password

def seed_everything(app):
    with app.app_context():
        print("Starting Mega Seeding...")

        # 1. Permissions & Roles
        print("Creating Roles & Permissions...")
        resources = ['devices', 'alerts', 'incidents', 'technicians', 'locations', 'vendors', 'maintenance', 'audit', 'reports']
        actions = ['read', 'write', 'delete', 'assign', 'resolve', 'export']
        
        for res in resources:
            for act in actions:
                name = f"{res}:{act}"
                if not Permission.query.filter_by(name=name).first():
                    db.session.add(Permission(name=name, resource=res, action=act, description=f"Can {act} {res}"))
        db.session.commit()

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', display_name='System Administrator', description='Full system access', is_system=True)
            db.session.add(admin_role)
            db.session.commit()
            admin_role.permissions = Permission.query.all()
            db.session.commit()

        # 2. Users
        print("Creating Admin User...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin', email='admin@teletrack.corp', full_name='System Administrator',
                password_hash=hash_password('admin123'), status='active', email_verified=True
            )
            admin.roles.append(admin_role)
            db.session.add(admin)
        else:
            admin.password_hash = hash_password('admin123')
            if admin_role not in admin.roles:
                admin.roles.append(admin_role)
        db.session.commit()
        admin_id = admin.id

        # 3. Org Structure
        print("Creating Org Structure...")
        if Department.query.count() == 0:
            net_ops = Department(name="Network Operations", description="Core infrastructure")
            db.session.add(net_ops)
            db.session.commit()
            db.session.add(Team(name="L1 Support", department_id=net_ops.id))
            db.session.add(Team(name="Backbone", department_id=net_ops.id))
            db.session.commit()

        # 4. Locations
        print("Creating Locations...")
        if Location.query.count() < 5:
            loc_data = [
                ("Alpha Datacenter", "Ashburn", "USA", "Tier 4"),
                ("London IX", "London", "UK", "Hub"),
                ("Tokyo Edge", "Tokyo", "Japan", "Edge Node"),
                ("Frankfurt Main", "Frankfurt", "Germany", "Backbone"),
                ("Sydney Regional", "Sydney", "Australia", "Regional")
            ]
            for name, city, country, stype in loc_data:
                if not Location.query.filter_by(location_name=name).first():
                    db.session.add(Location(location_name=name, city=city, country=country, site_type=stype, contact_person="Ops Team"))
            db.session.commit()
        all_locs = Location.query.all()

        # 5. Vendors
        print("Creating Vendors...")
        if Vendor.query.count() < 4:
            for v_name in ["Cisco", "Juniper", "Arista", "Palo Alto"]:
                if not Vendor.query.filter_by(vendor_name=v_name).first():
                    db.session.add(Vendor(vendor_name=v_name, country_of_origin="USA"))
            db.session.commit()
        all_vendors = Vendor.query.all()

        # 6. SLA Policies
        print("Creating SLA Policies...")
        for level, resp, res in [("critical", 15, 60), ("high", 30, 240), ("medium", 120, 720), ("low", 240, 1440)]:
            if not SLAPolicy.query.filter_by(severity_level=level).first():
                db.session.add(SLAPolicy(severity_level=level, response_time_minutes=resp, resolution_time_minutes=res))
        db.session.commit()

        # 7. Devices
        print("Creating Devices...")
        if Device.query.count() < 20:
            for i in range(25):
                v = random.choice(all_vendors)
                l = random.choice(all_locs)
                dt = random.choice(["Router", "Switch", "Firewall", "Server"])
                db.session.add(Device(
                    device_name=f"{l.city[:3].upper()}-{dt[:3].upper()}-{i+100}",
                    device_type=dt, location_id=l.id, vendor_id=v.id,
                    status=random.choice(["online", "online", "online", "degraded"]),
                    ip_address=f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                    cpu_usage=random.uniform(10, 90), memory_usage=random.uniform(20, 80)
                ))
            db.session.commit()
        all_devices = Device.query.all()

        # 8. Technicians
        print("Creating Technicians...")
        if Technician.query.count() < 4:
            for name in ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince"]:
                db.session.add(Technician(full_name=name, email=f"{name.lower().replace(' ', '.')}@teletrack.corp", status="available"))
            db.session.commit()
        all_techs = Technician.query.all()

        # 9. Alerts
        print("Creating Alerts...")
        if Alert.query.count() < 15:
            for i in range(20):
                dev = random.choice(all_devices)
                db.session.add(Alert(
                    device_id=dev.id, alert_type=random.choice(["Connectivity Loss", "Hardware Fault", "High Latency"]),
                    severity=random.choice(["critical", "high", "medium"]), status="open",
                    message="Automated monitoring alert triggered.", alert_time=datetime.now(timezone.utc) - timedelta(hours=i)
                ))
            db.session.commit()

        # 10. Incidents
        print("Creating Incidents...")
        if Incident.query.count() < 5:
            for title in ["Core Outage", "Fiber Cut", "BGP Hijack Attempt"]:
                db.session.add(Incident(title=title, description="Investigation in progress.", status="open", severity="critical", reported_by_id=admin_id))
            db.session.commit()

        # 11. Maintenance Logs
        print("Creating Maintenance Logs...")
        if MaintenanceLog.query.count() < 10:
            for i in range(12):
                dev = random.choice(all_devices)
                tech = random.choice(all_techs)
                db.session.add(MaintenanceLog(
                    device_id=dev.id, technician_id=tech.id, maintenance_type="Firmware Patch",
                    description="Applied monthly security patch.", outcome="Success",
                    completed_date=datetime.now(timezone.utc) - timedelta(days=i)
                ))
            db.session.commit()

        # 12. Network Links
        from models.supporting import NetworkLink
        print("Creating Network Links...")
        if NetworkLink.query.count() < 10:
            for i in range(15):
                d1 = random.choice(all_devices)
                d2 = random.choice(all_devices)
                if d1.id != d2.id:
                    db.session.add(NetworkLink(source_device_id=d1.id, target_device_id=d2.id, link_type="Fiber", bandwidth="100 Gbps", status="active"))
            db.session.commit()

        # 13. Audit Logs
        print("Creating Audit Logs...")
        if AuditLog.query.count() < 20:
            for i in range(30):
                db.session.add(AuditLog(user_id=admin_id, action="SYS_INIT", resource="database", timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*10)))
            db.session.commit()

        print("Mega Seeding Complete! System is fully populated.")

if __name__ == "__main__":
    from app import create_app
    seed_everything(create_app())
