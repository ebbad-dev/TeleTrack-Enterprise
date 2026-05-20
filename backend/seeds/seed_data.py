"""
TeleTrack Enterprise  Production Seed Data
Seeds the database with roles, permissions, admin user, and comprehensive sample data.
Consolidated from seed_data.py + mega_seed.py into a single authoritative seeder.
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from auth.utils import hash_password


def seed_permissions():
    """Create all permission records."""
    from models.user import Permission

    resources = {
        "devices": ["read", "write", "delete"],
        "alerts": ["read", "write", "assign", "resolve", "delete"],
        "incidents": ["read", "write", "escalate", "delete"],
        "technicians": ["read", "write", "delete"],
        "locations": ["read", "write", "delete"],
        "vendors": ["read", "write", "delete"],
        "maintenance": ["read", "write", "delete"],
        "network": ["read", "write", "delete"],
        "users": ["read", "write", "manage_roles", "delete"],
        "reports": ["read", "generate"],
        "audit": ["read"],
        "settings": ["read", "write"],
        "notifications": ["read", "write"],
    }

    count = 0
    for resource, actions in resources.items():
        for action in actions:
            name = f"{resource}:{action}"
            if not Permission.query.filter_by(name=name).first():
                db.session.add(Permission(name=name, resource=resource, action=action,
                               description=f"{action.title()} {resource}"))
                count += 1
    db.session.commit()
    print(f"   {count} permissions created")


def seed_roles():
    """Create system roles with appropriate permissions."""
    from models.user import Role, Permission

    role_defs = {
        "super_admin": {
            "display_name": "Super Admin",
            "description": "Full system access  all permissions",
            "permissions": None,  # All permissions
        },
        "admin": {
            "display_name": "System Administrator",
            "description": "Administrative access",
            "permissions": None,  # All permissions
        },
        "network_admin": {
            "display_name": "Network Admin",
            "description": "Network infrastructure management",
            "permissions": [
                "devices:*", "alerts:*", "incidents:*", "technicians:*",
                "locations:*", "vendors:*", "maintenance:*", "network:*",
                "reports:*", "audit:read", "notifications:*",
            ],
        },
        "noc_operator": {
            "display_name": "NOC Operator",
            "description": "Network Operations Center operator",
            "permissions": [
                "devices:read", "alerts:read", "alerts:write", "alerts:assign",
                "alerts:resolve", "incidents:read", "incidents:write",
                "technicians:read", "locations:read", "vendors:read",
                "maintenance:read", "network:read", "reports:read",
                "notifications:read", "notifications:write",
            ],
        },
        "technician": {
            "display_name": "Technician",
            "description": "Field technician",
            "permissions": [
                "devices:read", "alerts:read", "alerts:write", "alerts:resolve",
                "incidents:read", "maintenance:read", "maintenance:write",
                "notifications:read",
            ],
        },
        "it_manager": {
            "display_name": "IT Manager",
            "description": "IT department manager",
            "permissions": [
                "devices:read", "alerts:read", "incidents:read", "incidents:write",
                "technicians:read", "locations:read", "vendors:read",
                "maintenance:read", "network:read", "reports:read",
                "reports:generate", "audit:read", "notifications:read",
            ],
        },
        "security_auditor": {
            "display_name": "Security Auditor",
            "description": "Security and compliance auditor",
            "permissions": [
                "devices:read", "alerts:read", "incidents:read",
                "audit:read", "reports:read", "reports:generate",
                "notifications:read",
            ],
        },
    }

    all_perms = Permission.query.all()
    perm_map = {p.name: p for p in all_perms}
    count = 0

    for role_name, role_def in role_defs.items():
        existing = Role.query.filter_by(name=role_name).first()
        if existing:
            continue

        role = Role(name=role_name, display_name=role_def["display_name"],
                    description=role_def["description"], is_system=True)

        if role_def["permissions"] is None:
            role.permissions = all_perms
        else:
            for perm_pattern in role_def["permissions"]:
                if perm_pattern.endswith(":*"):
                    resource = perm_pattern.split(":")[0]
                    for p in all_perms:
                        if p.resource == resource:
                            role.permissions.append(p)
                elif perm_pattern in perm_map:
                    role.permissions.append(perm_map[perm_pattern])

        db.session.add(role)
        count += 1

    db.session.commit()
    print(f"   {count} roles created")


def seed_admin_user():
    """Create the initial admin user."""
    from models.user import User, Role

    admin = User.query.filter_by(username="admin").first()
    admin_role = Role.query.filter_by(name="super_admin").first()
    backup_role = Role.query.filter_by(name="admin").first()

    if admin:
        # Ensure password is standardized and roles are assigned
        admin.password_hash = hash_password("admin123")
        if admin_role and admin_role not in admin.roles:
            admin.roles.append(admin_role)
        if backup_role and backup_role not in admin.roles:
            admin.roles.append(backup_role)
        db.session.commit()
        print("   Admin user updated (admin / admin123)")
        return

    admin = User(
        username="admin",
        email="admin@teletrack.com",
        password_hash=hash_password("admin123"),
        full_name="System Administrator",
        status="active",
        email_verified=True,
    )
    if admin_role:
        admin.roles.append(admin_role)
    if backup_role:
        admin.roles.append(backup_role)

    db.session.add(admin)
    db.session.commit()
    print("   Admin user created (admin / admin123)")


def seed_sla_policies():
    """Create default SLA policies."""
    from models.supporting import SLAPolicy

    policies = [
        ("critical", 15, 60, True),
        ("high", 30, 240, True),
        ("medium", 60, 480, False),
        ("low", 120, 1440, False),
    ]
    for severity, resp, res, esc in policies:
        if not SLAPolicy.query.filter_by(severity_level=severity).first():
            db.session.add(SLAPolicy(severity_level=severity, response_time_minutes=resp,
                                     resolution_time_minutes=res, escalation_required=esc))
    db.session.commit()
    print("   SLA policies created")


def seed_org_structure():
    """Create departments and teams."""
    from models.supporting import Department, Team

    if Department.query.count() == 0:
        depts = [
            ("Network Operations", "Core infrastructure management"),
            ("Security Operations", "Cybersecurity and threat detection"),
            ("Cloud Services", "Cloud infrastructure and SaaS"),
        ]
        for name, desc in depts:
            db.session.add(Department(name=name, description=desc))
        db.session.commit()

        net_ops = Department.query.filter_by(name="Network Operations").first()
        if net_ops:
            for tname in ["L1 Support", "Backbone Engineering", "Edge Computing"]:
                db.session.add(Team(name=tname, department_id=net_ops.id))
            db.session.commit()
    print("   Org structure created")


def seed_sample_data():
    """Create sample vendors, locations, technicians, devices, alerts, incidents, network links."""
    from models.supporting import Vendor, Location, Technician, NetworkLink, MaintenanceLog
    from models.device import Device
    from models.alert import Alert
    from models.incident import Incident
    from models.user import User

    #  VENDORS 
    vendors_data = [
        ("Cisco Systems", "USA", "support@cisco.com", "+1-800-553-6387", "https://cisco.com"),
        ("Fortinet", "USA", "support@fortinet.com", "+1-408-235-7700", "https://fortinet.com"),
        ("Huawei Technologies", "China", "enterprise@huawei.com", "+86-755-2878-0808", "https://huawei.com"),
        ("Juniper Networks", "USA", "support@juniper.net", "+1-888-314-5822", "https://juniper.net"),
        ("Dell Technologies", "USA", "support@dell.com", "+1-800-624-9897", "https://dell.com"),
        ("HP Enterprise", "USA", "support@hpe.com", "+1-800-474-6836", "https://hpe.com"),
        ("MikroTik", "Latvia", "support@mikrotik.com", "+371-6731-6212", "https://mikrotik.com"),
        ("Palo Alto Networks", "USA", "support@paloalto.com", "+1-866-320-4788", "https://paloaltonetworks.com"),
    ]
    for v in vendors_data:
        if not Vendor.query.filter_by(vendor_name=v[0]).first():
            db.session.add(Vendor(vendor_name=v[0], country_of_origin=v[1], support_email=v[2],
                                  support_phone=v[3], website=v[4]))
    db.session.commit()
    print("   Vendors seeded")

    #  LOCATIONS 
    locs_data = [
        ("HQ - Karachi", "Karachi", "Pakistan", "Headquarters", "I.I Chundrigar Road", "Muhammad Usman", "+92-300-1234567"),
        ("DC - Lahore", "Lahore", "Pakistan", "Data Center", "Gulberg III", "Sara Ahmed", "+92-300-7654321"),
        ("Branch - Islamabad", "Islamabad", "Pakistan", "Branch Office", "Blue Area", "Bilal Khan", "+92-300-1112223"),
        ("Hub - Faisalabad", "Faisalabad", "Pakistan", "Network Hub", "Canal Road", "Fatima Hassan", "+92-300-4445556"),
        ("Node - Peshawar", "Peshawar", "Pakistan", "Network Node", "University Road", "Ali Raza", "+92-300-7778889"),
        ("Site - Quetta", "Quetta", "Pakistan", "Remote Site", "Jinnah Road", "Ayesha Malik", "+92-300-9990000"),
        ("Alpha Datacenter", "Ashburn", "USA", "Tier 4", "Loudoun County Tech Corridor", "Ops Team", "+1-800-555-0001"),
        ("London IX", "London", "UK", "Hub", "Docklands", "Ops Team", "+44-20-5555-0001"),
    ]
    for l in locs_data:
        if not Location.query.filter_by(location_name=l[0]).first():
            db.session.add(Location(location_name=l[0], city=l[1], country=l[2], site_type=l[3],
                                    address_line=l[4], contact_person=l[5], contact_phone=l[6]))
    db.session.commit()
    print("   Locations seeded")

    #  TECHNICIANS 
    techs_data = [
        ("Usman Ahmed", "usman.ahmed@teletrack.pk", "+92-312-5556667", "Network Security", "Morning", "available"),
        ("Sara Khan", "sara.khan@teletrack.pk", "+92-312-5556668", "Cloud Infrastructure", "Evening", "busy"),
        ("Bilal Siddiqui", "bilal.s@teletrack.pk", "+92-312-5556669", "Wireless Networks", "Night", "available"),
        ("Fatima Ali", "fatima.ali@teletrack.pk", "+92-312-5556670", "Optical Fiber", "Flexible", "on_leave"),
        ("Ali Hassan", "ali.h@teletrack.pk", "+92-312-5556671", "VoIP Systems", "Morning", "available"),
        ("Ayesha Bibi", "ayesha.b@teletrack.pk", "+92-312-5556672", "Data Center Ops", "Evening", "available"),
    ]
    for t in techs_data:
        if not Technician.query.filter_by(email=t[1]).first():
            db.session.add(Technician(full_name=t[0], email=t[1], phone=t[2],
                                      specialization=t[3], shift=t[4], status=t[5]))
    db.session.commit()
    print("   Technicians seeded")

    #  DEVICES 
    all_vendors = Vendor.query.all()
    all_locs = Location.query.all()
    dev_types = ["Router", "Switch", "Firewall", "Server", "Access Point"]

    if Device.query.count() < 50:
        for i in range(1, 51):
            name = f"KHI-NODE-{i:02d}"
            if not Device.query.filter_by(device_name=name).first():
                db.session.add(Device(
                    device_name=name,
                    device_type=random.choice(dev_types),
                    vendor_id=all_vendors[i % len(all_vendors)].id if all_vendors else None,
                    model=f"Model-X{i}",
                    ip_address=f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                    mac_address=f"00:50:56:AB:{random.randint(10,99)}:{i:02X}",
                    location_id=all_locs[i % len(all_locs)].id if all_locs else 1,
                    status=random.choice(["online", "online", "online", "degraded", "offline"]),
                    monitoring_enabled=True,
                    cpu_usage=round(random.uniform(10, 90), 1),
                    memory_usage=round(random.uniform(20, 80), 1),
                    temperature=round(random.uniform(25, 55), 1),
                ))
        db.session.commit()
    print("   Devices seeded")

    #  ALERTS 
    all_devices = Device.query.all()
    all_techs = Technician.query.all()

    if Alert.query.count() < 30:
        alert_types = [
            ("High CPU Usage", "critical", "Router CPU is at 98%  immediate action required"),
            ("Link Down", "high", "Fiber link between nodes is down"),
            ("Auth Failure", "medium", "Repeated failed login attempts detected"),
            ("Temperature High", "high", "Server room temperature exceeded 35C"),
            ("Memory Leak", "medium", "Switch memory usage increasing rapidly"),
            ("Fan Failure", "critical", "Cooling fan stopped on core switch"),
            ("Connectivity Loss", "high", "Intermittent packet loss on backbone"),
            ("Hardware Fault", "critical", "RAID controller degraded"),
            ("High Latency", "medium", "Response time exceeded 200ms threshold"),
            ("Firmware Outdated", "low", "Device firmware is 6+ months behind"),
            ("Bandwidth Saturated", "high", "Uplink interface is running at 99% capacity"),
            ("BGP Peer Down", "critical", "BGP session to upstream provider dropped"),
            ("Power Supply Failure", "high", "Redundant power supply unit A failed"),
            ("Disk Space Low", "medium", "System partition is 95% full"),
            ("Malware Detected", "critical", "Suspicious traffic pattern matched botnet signature"),
        ]
        # Generate 30 alerts
        for i in range(30):
            atype, sev, msg = random.choice(alert_types)
            dev = random.choice(all_devices)
            tech = random.choice(all_techs) if all_techs else None
            db.session.add(Alert(
                device_id=dev.id, assigned_tech_id=tech.id if tech else None,
                alert_type=atype, severity=sev, message=msg, status="open",
                alert_time=datetime.now(timezone.utc) - timedelta(hours=i * 2),
            ))
        db.session.commit()
    print("   Alerts seeded")

    #  INCIDENTS 
    admin = User.query.filter_by(username="admin").first()
    admin_id = admin.id if admin else 1

    if Incident.query.count() < 15:
        incidents = [
            ("Core Network Outage", "Major backbone failure affecting all eastern region nodes", "critical"),
            ("Fiber Cut  Lahore Link", "Physical fiber damage on trunk route between HQ and DC", "high"),
            ("BGP Hijack Attempt", "Suspicious BGP route announcement detected from unknown AS", "critical"),
            ("SAN Storage Failure", "Primary SAN array degraded  DR failover initiated", "high"),
            ("Cooling System Failure", "Data center HVAC unit 2 stopped responding", "high"),
            ("DDoS Attack on Edge", "Volumetric DDoS attack mitigating at edge firewalls", "critical"),
            ("Database Sync Lag", "Replica sync lagging by 45 minutes", "medium"),
            ("SSL Certificate Expiry", "Wildcard cert expiring in 48 hours", "high"),
        ]
        for i in range(15):
            title, desc, sev = random.choice(incidents)
            db.session.add(Incident(title=title, description=desc, status=random.choice(["open", "acknowledged", "resolved"]),
                                    severity=sev, reported_by_id=admin_id))
        db.session.commit()
    print("   Incidents seeded")

    #  MAINTENANCE LOGS 
    if MaintenanceLog.query.count() < 30:
        for i in range(30):
            dev = random.choice(all_devices)
            tech = random.choice(all_techs) if all_techs else None
            db.session.add(MaintenanceLog(
                device_id=dev.id, technician_id=tech.id if tech else None,
                maintenance_type=random.choice(["Firmware Patch", "Hardware Replacement", "Preventive", "Configuration Change"]),
                description="Scheduled maintenance completed successfully.",
                outcome="Success",
                completed_date=datetime.now(timezone.utc) - timedelta(days=i),
            ))
        db.session.commit()
    print("   Maintenance logs seeded")

    #  NETWORK LINKS 
    from models.supporting import NetworkLink
    if NetworkLink.query.count() < 40:
        link_types = ["Fiber", "Ethernet", "MPLS", "VPN Tunnel", "Wireless Bridge"]
        used_pairs = set()
        for _ in range(60):
            d1 = random.choice(all_devices)
            d2 = random.choice(all_devices)
            pair = (min(d1.id, d2.id), max(d1.id, d2.id))
            if d1.id != d2.id and pair not in used_pairs:
                used_pairs.add(pair)
                db.session.add(NetworkLink(
                    source_device_id=d1.id, target_device_id=d2.id,
                    link_type=random.choice(link_types),
                    bandwidth=random.choice(["1 Gbps", "10 Gbps", "100 Gbps", "400 Gbps"]),
                    status=random.choice(["active", "active", "active", "degraded", "down"]),
                ))
        db.session.commit()
    print("   Network links seeded")

    #  AUDIT LOGS 
    from models.supporting import AuditLog
    if AuditLog.query.count() < 100:
        for i in range(100):
            db.session.add(AuditLog(
                user_id=admin_id, action=random.choice(["LOGIN", "DEVICE_CREATE", "ALERT_RESOLVE", "CONFIG_CHANGE", "USER_UPDATE", "REPORT_GENERATE"]),
                resource=random.choice(["devices", "alerts", "auth", "system", "users"]),
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=i * 15),
            ))
        db.session.commit()
    print("   Audit logs seeded")


def seed_all():
    """Run all seed functions."""
    print("\n" + "" * 55)
    print("  TeleTrack Enterprise  Database Seeding")
    print("" * 55 + "\n")

    seed_permissions()
    seed_roles()
    seed_admin_user()
    seed_sla_policies()
    seed_org_structure()
    seed_sample_data()

    print("\n   All seed data loaded successfully!")
    print("  Login: admin / admin123\n")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_all()
