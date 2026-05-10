"""
TeleTrack Enterprise — Production Seed Data
Seeds the database with roles, permissions, initial admin user, and sample data.
"""

import sys
import os

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

    perms = []
    for resource, actions in resources.items():
        for action in actions:
            name = f"{resource}:{action}"
            existing = Permission.query.filter_by(name=name).first()
            if not existing:
                p = Permission(name=name, resource=resource, action=action, description=f"{action.title()} {resource}")
                db.session.add(p)
                perms.append(name)

    db.session.commit()
    print(f"  ✓ {len(perms)} permissions created")
    return perms


def seed_roles():
    """Create system roles with appropriate permissions."""
    from models.user import Role, Permission

    role_defs = {
        "super_admin": {
            "display_name": "Super Admin",
            "description": "Full system access",
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

    for role_name, role_def in role_defs.items():
        existing = Role.query.filter_by(name=role_name).first()
        if existing:
            continue

        role = Role(name=role_name, display_name=role_def["display_name"],
                    description=role_def["description"], is_system=True)

        if role_def["permissions"] is None:
            # Super admin gets all
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

    db.session.commit()
    print(f"  ✓ {len(role_defs)} roles created")


def seed_admin_user():
    """Create the initial admin user."""
    from models.user import User, Role

    existing = User.query.filter_by(username="admin").first()
    if existing:
        print("  ✓ Admin user already exists")
        return

    admin_role = Role.query.filter_by(name="super_admin").first()

    admin = User(
        username="admin",
        email="admin@teletrack.com",
        password_hash=hash_password("TeleTrack@2026"),
        full_name="System Administrator",
        status="active",
        email_verified=True,
    )
    if admin_role:
        admin.roles.append(admin_role)

    db.session.add(admin)
    db.session.commit()
    print("  ✓ Admin user created (admin / TeleTrack@2026)")


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
        existing = SLAPolicy.query.filter_by(severity_level=severity).first()
        if not existing:
            db.session.add(SLAPolicy(severity_level=severity, response_time_minutes=resp,
                                     resolution_time_minutes=res, escalation_required=esc))
    db.session.commit()
    print("  ✓ SLA policies created")


def seed_sample_data():
    """Create sample vendors, locations, technicians, devices, and alerts."""
    from models.supporting import Vendor, Location, Technician
    from models.device import Device
    from models.alert import Alert
    from datetime import datetime, timezone

    # Vendors
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
            db.session.add(Vendor(vendor_name=v[0], country_of_origin=v[1], support_email=v[2], support_phone=v[3], website=v[4]))
    db.session.commit()
    print("  ✓ Vendors seeded")

    # Locations
    locs_data = [
        ("HQ - Karachi", "Karachi", "Pakistan", "Headquarters", "I.I Chundrigar Road", "Muhammad Usman", "+92-300-1234567"),
        ("DC - Lahore", "Lahore", "Pakistan", "Data Center", "Gulberg III", "Sara Ahmed", "+92-300-7654321"),
        ("Branch - Islamabad", "Islamabad", "Pakistan", "Branch Office", "Blue Area", "Bilal Khan", "+92-300-1112223"),
        ("Hub - Faisalabad", "Faisalabad", "Pakistan", "Network Hub", "Canal Road", "Fatima Hassan", "+92-300-4445556"),
        ("Node - Peshawar", "Peshawar", "Pakistan", "Network Node", "University Road", "Ali Raza", "+92-300-7778889"),
        ("Site - Quetta", "Quetta", "Pakistan", "Remote Site", "Jinnah Road", "Ayesha Malik", "+92-300-9990000"),
    ]
    for l in locs_data:
        if not Location.query.filter_by(location_name=l[0]).first():
            db.session.add(Location(location_name=l[0], city=l[1], country=l[2], site_type=l[3], address_line=l[4], contact_person=l[5], contact_phone=l[6]))
    db.session.commit()
    print("  ✓ Locations seeded")

    # Technicians
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
            db.session.add(Technician(full_name=t[0], email=t[1], phone=t[2], specialization=t[3], shift=t[4], status=t[5]))
    db.session.commit()
    print("  ✓ Technicians seeded")

    # Devices
    import random
    dev_types = ["Router", "Switch", "Firewall", "Server", "Access Point"]
    all_vendors = Vendor.query.all()
    all_locs = Location.query.all()
    for i in range(1, 13):
        name = f"KHI-NODE-{i:02d}"
        if not Device.query.filter_by(device_name=name).first():
            db.session.add(Device(
                device_name=name, device_type=random.choice(dev_types),
                vendor_id=all_vendors[i % len(all_vendors)].id if all_vendors else None,
                model=f"Model-X{i}", ip_address=f"10.0.0.{10+i}",
                mac_address=f"00:50:56:AB:CD:{i:02X}",
                location_id=all_locs[i % len(all_locs)].id if all_locs else 1,
                status="online", monitoring_enabled=True,
            ))
    db.session.commit()
    print("  ✓ Devices seeded")

    # Alerts
    alerts_data = [
        (1, "High CPU Usage", "critical", "Router CPU is at 98%"),
        (2, "Link Down", "high", "Fiber link between Node 1 and 2 is down"),
        (3, "Auth Failure", "medium", "Repeated failed login attempts from 10.0.0.50"),
        (4, "Temp High", "high", "Server room temperature exceeded 35°C"),
        (5, "Memory Leak", "medium", "Switch memory usage increasing rapidly"),
        (6, "Fan Failure", "critical", "Cooling fan stopped on core switch"),
    ]
    all_devices = Device.query.all()
    all_techs = Technician.query.all()
    for a in alerts_data:
        dev_id = all_devices[a[0] - 1].id if len(all_devices) >= a[0] else 1
        tech_id = all_techs[(a[0] - 1) % len(all_techs)].id if all_techs else None
        if not Alert.query.filter_by(device_id=dev_id, alert_type=a[1]).first():
            db.session.add(Alert(device_id=dev_id, assigned_tech_id=tech_id,
                                alert_type=a[1], severity=a[2], message=a[3], status="open"))
    db.session.commit()
    print("  ✓ Alerts seeded")


def seed_all():
    """Run all seed functions."""
    print("\n" + "=" * 50)
    print("  TeleTrack Enterprise — Database Seeding")
    print("=" * 50 + "\n")

    seed_permissions()
    seed_roles()
    seed_admin_user()
    seed_sla_policies()
    seed_sample_data()

    print("\n  ✅ All seed data loaded successfully!")
    print("  Login: admin / TeleTrack@2026\n")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_all()
