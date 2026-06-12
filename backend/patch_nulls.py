"""
TeleTrack Enterprise — Database Null Patching Script
Ensures no seeded or existing data fields are null by filling all nullable columns with premium, coherent mock data.
"""

import sys
import os
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import Device, Technician, Location, MaintenanceLog, Alert, Incident, Vendor

def patch_database():
    print("==================================================")
    print("PATCHING TELETRACK DATABASE NULL FIELDS WITH PREMIUM DATA")
    print("==================================================")

    # 1. Patch Vendors
    vendors = Vendor.query.all()
    print(f"Checking {len(vendors)} vendors...")
    for v in vendors:
        if not v.country_of_origin:
            v.country_of_origin = random.choice(["USA", "Germany", "Japan", "UK"])
        if not v.support_email:
            v.support_email = f"support@{v.vendor_name.lower().replace(' ', '')}.com"
        if not v.support_phone:
            v.support_phone = f"+1-800-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        if not v.website:
            v.website = f"https://www.{v.vendor_name.lower().replace(' ', '')}.com"
    
    # 2. Patch Locations
    locations = Location.query.all()
    print(f"Checking {len(locations)} locations...")
    for l in locations:
        if not l.city:
            l.city = "Karachi"
        if not l.country:
            l.country = "Pakistan"
        if not l.site_type:
            l.site_type = random.choice(["Data Center", "Headquarters", "Network Node", "Branch Office"])
        if not l.address_line:
            l.address_line = f"Plot {random.randint(1, 150)}, Tech Zone"
        if not l.contact_person:
            l.contact_person = random.choice(["Ali Shah", "Zainab Malik", "Hamza Khan", "Fatima Jamil"])
        if not l.contact_phone:
            l.contact_phone = f"+92-300-{random.randint(1000000, 9999999)}"
        if not l.image_url:
            l.image_url = f"https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=400&q=80"

    # 3. Patch Technicians
    techs = Technician.query.all()
    print(f"Checking {len(techs)} technicians...")
    for t in techs:
        if not t.email:
            t.email = f"{t.full_name.lower().replace(' ', '.')}@teletrack.pk"
        if not t.phone:
            t.phone = f"+92-312-{random.randint(1000000, 9999999)}"
        if not t.specialization:
            t.specialization = random.choice(["Core Routing", "Cloud Virtualization", "Next-Gen Firewall", "Fiber Optics"])
        if not t.shift:
            t.shift = random.choice(["Morning", "Evening", "Night", "Flexible"])
        if not t.image_url:
            t.image_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={t.full_name.replace(' ', '')}&backgroundColor=0a0a0f"

    # 4. Patch Devices
    devices = Device.query.all()
    print(f"Checking {len(devices)} devices...")
    for d in devices:
        if not d.model:
            d.model = f"Catalyst-X{random.randint(1000, 9999)}"
        if not d.serial_number:
            d.serial_number = f"SN-TTL-{random.randint(100000, 999999)}"
        if not d.firmware_version:
            d.firmware_version = f"v{random.randint(12, 17)}.{random.randint(1, 5)}.{random.randint(0, 9)}"
        if not d.installed_date:
            d.installed_date = datetime.now(timezone.utc) - timedelta(days=random.randint(30, 730))
        if not d.notes or d.notes.strip() == "":
            d.notes = f"Primary {d.device_type} serving critical network plane. Regularly patched and monitored."
        if not d.snmp_community:
            d.snmp_community = "public"
        if not d.image_url:
            d.image_url = f"https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=400&q=80"
        
        # Ensure location and vendor are linked
        if not d.location_id and locations:
            d.location_id = random.choice(locations).id
        if not d.vendor_id and vendors:
            d.vendor_id = random.choice(vendors).id

    # 5. Patch Maintenance Logs
    logs = MaintenanceLog.query.all()
    print(f"Checking {len(logs)} maintenance logs...")
    for m in logs:
        if not m.maintenance_type:
            m.maintenance_type = random.choice(["Preventive", "Firmware Patch", "Hardware Replacement", "Config Audit"])
        if not m.description or m.description == "Scheduled maintenance completed successfully.":
            m.description = f"Completed scheduled {m.maintenance_type.lower()} checklist. Verified power redundancy, ran interface diagnostics, and verified system logs."
        if not m.duration_minutes:
            m.duration_minutes = random.choice([30, 45, 60, 90, 120])
        if not m.outcome:
            m.outcome = "Success"
        if not m.notes:
            m.notes = "Zero warnings encountered. Backups verified prior to execution."
        if not m.completed_date:
            m.completed_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))

    # 6. Patch Incidents
    incidents = Incident.query.all()
    print(f"Checking {len(incidents)} incidents...")
    for inc in incidents:
        if not inc.impact:
            inc.impact = f"High availability failover triggered for {random.randint(5, 25)} nodes."
        if not inc.affected_services:
            inc.affected_services = "Active Directory, SAP ERP, Internal NOC Dashboard"
        if not inc.root_cause:
            inc.root_cause = "Hardware controller failure on redundant backbone route" if inc.severity == "critical" else "Transient packet drop during high throughput period"
        if not inc.resolution_summary:
            inc.resolution_summary = "Replaced degraded component and re-routed optical transit path. Verified routing convergence."
        if not inc.lessons_learned:
            inc.lessons_learned = "Add passive redundant path to bypass primary optical trunk."

    db.session.commit()
    print("==================================================")
    print("DATABASE PATCHED SUCCESSFULLY! ALL FIELDS FULLY POPULATED.")
    print("==================================================")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        patch_database()
