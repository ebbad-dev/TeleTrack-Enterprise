from app import execute_query
from datetime import datetime, timedelta
import random

print("=== SEEDING EMPTY TABLES ===\n")

# 1. Users
print("1. Users...")
users = [
    ("admin_user", "pbkdf2:sha256:hash1", "Muhammad Usman", "usman@teletrack.pk", "Admin", "Active"),
    ("tech_lead", "pbkdf2:sha256:hash2", "Sara Ahmed", "sara@teletrack.pk", "Manager", "Active"),
    ("field_tech1", "pbkdf2:sha256:hash3", "Bilal Khan", "bilal@teletrack.pk", "Technician", "Active"),
    ("viewer01", "pbkdf2:sha256:hash4", "Fatima Hassan", "fatima@teletrack.pk", "Viewer", "Active"),
    ("noc_ops", "pbkdf2:sha256:hash5", "Ali Raza", "ali.raza@teletrack.pk", "Technician", "Active"),
    ("sec_admin", "pbkdf2:sha256:hash6", "Ayesha Malik", "ayesha@teletrack.pk", "Admin", "Active"),
    ("net_eng", "pbkdf2:sha256:hash7", "Omar Farooq", "omar@teletrack.pk", "Technician", "Inactive"),
    ("mgr_ops", "pbkdf2:sha256:hash8", "Zainab Tariq", "zainab@teletrack.pk", "Manager", "Active"),
]
for u in users:
    try:
        execute_query(
            "INSERT INTO Users (Username, PasswordHash, FullName, Email, Role, Status, CreatedAt) VALUES (?,?,?,?,?,?,GETDATE())",
            list(u)
        )
    except Exception as e:
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower() or 'violation' in str(e).lower():
            pass
        else:
            print(f"  Warning: {e}")
print(f"  Done - {len(users)} users")

# 2. Vendors
print("2. Vendors...")
vendors = [
    ("Cisco Systems", "USA", "support@cisco.com", "+1-800-553-6387", "https://cisco.com"),
    ("Fortinet", "USA", "support@fortinet.com", "+1-408-235-7700", "https://fortinet.com"),
    ("Huawei Technologies", "China", "enterprise@huawei.com", "+86-755-2878-0808", "https://huawei.com"),
    ("Juniper Networks", "USA", "support@juniper.net", "+1-888-314-5822", "https://juniper.net"),
    ("Dell Technologies", "USA", "support@dell.com", "+1-800-624-9897", "https://dell.com"),
    ("HP Enterprise", "USA", "support@hpe.com", "+1-800-474-6836", "https://hpe.com"),
    ("MikroTik", "Latvia", "support@mikrotik.com", "+371-6731-6212", "https://mikrotik.com"),
    ("Palo Alto Networks", "USA", "support@paloalto.com", "+1-866-320-4788", "https://paloaltonetworks.com"),
]
for v in vendors:
    try:
        execute_query(
            "INSERT INTO Vendors (VendorName, CountryOfOrigin, SupportEmail, SupportPhone, Website, CreatedAt) VALUES (?,?,?,?,?,GETDATE())",
            list(v)
        )
    except Exception as e:
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower() or 'violation' in str(e).lower():
            pass
        else:
            print(f"  Warning: {e}")
print(f"  Done - {len(vendors)} vendors")

# 2.1 Locations
print("2.1 Locations...")
locations = [
    ("HQ - Karachi", "Karachi", "Pakistan", "Headquarters", "I.I Chundrigar Road", "Muhammad Usman", "+92-300-1234567"),
    ("DC - Lahore", "Lahore", "Pakistan", "Data Center", "Gulberg III", "Sara Ahmed", "+92-300-7654321"),
    ("Branch - Islamabad", "Islamabad", "Pakistan", "Branch Office", "Blue Area", "Bilal Khan", "+92-300-1112223"),
    ("Hub - Faisalabad", "Faisalabad", "Pakistan", "Network Hub", "Canal Road", "Fatima Hassan", "+92-300-4445556"),
    ("Node - Peshawar", "Peshawar", "Pakistan", "Network Node", "University Road", "Ali Raza", "+92-300-7778889"),
    ("Site - Quetta", "Quetta", "Pakistan", "Remote Site", "Jinnah Road", "Ayesha Malik", "+92-300-9990000"),
]
for l in locations:
    try:
        execute_query(
            "INSERT INTO Locations (LocationName, City, Country, SiteType, AddressLine, ContactPerson, ContactPhone, CreatedAt) VALUES (?,?,?,?,?,?,?,GETDATE())",
            list(l)
        )
    except Exception as e:
        if 'duplicate' not in str(e).lower(): print(f"  Warning: {e}")
print(f"  Done - {len(locations)} locations")

# 2.2 Technicians
print("2.2 Technicians...")
techs = [
    ("Usman Ahmed", "usman.ahmed@teletrack.pk", "+92-312-5556667", "Network Security", "Morning", "Available"),
    ("Sara Khan", "sara.khan@teletrack.pk", "+92-312-5556668", "Cloud Infrastructure", "Evening", "Busy"),
    ("Bilal Siddiqui", "bilal.s@teletrack.pk", "+92-312-5556669", "Wireless Networks", "Night", "Available"),
    ("Fatima Ali", "fatima.ali@teletrack.pk", "+92-312-5556670", "Optical Fiber", "Flexible", "On Leave"),
    ("Ali Hassan", "ali.h@teletrack.pk", "+92-312-5556671", "VoIP Systems", "Morning", "Available"),
    ("Ayesha Bibi", "ayesha.b@teletrack.pk", "+92-312-5556672", "Data Center Ops", "Evening", "Available"),
]
for t in techs:
    try:
        execute_query(
            "INSERT INTO Technicians (FullName, Email, Phone, Specialization, Shift, Status, CreatedAt) VALUES (?,?,?,?,?,?,GETDATE())",
            list(t)
        )
    except Exception as e:
        if 'duplicate' not in str(e).lower(): print(f"  Warning: {e}")
print(f"  Done - {len(techs)} technicians")

# 3. SLA_Policies
print("3. SLA_Policies...")
sla = [
    ("Critical", 15, 60, 1),
    ("High", 30, 120, 1),
    ("Medium", 60, 480, 0),
    ("Low", 120, 1440, 0),
]
for s in sla:
    try:
        execute_query(
            "INSERT INTO SLA_Policies (SeverityLevel, ResponseTimeMinutes, ResolutionTimeMinutes, EscalationRequired, CreatedAt) VALUES (?,?,?,?,GETDATE())",
            list(s)
        )
    except Exception as e:
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower() or 'violation' in str(e).lower():
            pass
        else:
            print(f"  Warning: {e}")
print(f"  Done - {len(sla)} policies")

# 3.1 Devices
print("3.1 Devices...")
dev_types = ['Router', 'Switch', 'Firewall', 'Server', 'Access Point']
devices = []
for i in range(1, 13):
    name = f"KHI-NODE-{i:02d}"
    dtype = random.choice(dev_types)
    ip = f"10.0.0.{10+i}"
    mac = f"00:50:56:AB:CD:{i:02X}"
    loc_id = (i % 6) + 1
    vendor_id = (i % 8) + 1
    devices.append((name, dtype, vendor_id, f"Model-X{i}", ip, mac, loc_id, "Online"))

for d in devices:
    try:
        execute_query(
            "INSERT INTO Devices (DeviceName, DeviceType, VendorID, Model, IPAddress, MACAddress, LocationID, Status, InstalledDate) VALUES (?,?,?,?,?,?,?,?,CAST(GETDATE() AS DATE))",
            list(d)
        )
    except Exception as e:
        if 'duplicate' not in str(e).lower(): print(f"  Warning: {e}")
print(f"  Done - {len(devices)} devices")

# 3.2 Alerts
print("3.2 Alerts...")
alerts = [
    (1, 1, "High CPU Usage", "Critical", "Router CPU is at 98%", "Assigned"),
    (2, 2, "Link Down", "High", "Fiber link between Node 1 and 2 is down", "Open"),
    (3, 3, "Auth Failure", "Medium", "Repeated failed login attempts from 10.0.0.50", "In Progress"),
    (4, 4, "Temp High", "High", "Server room temperature exceeded 35C", "Open"),
    (5, 5, "Memory Leak", "Medium", "Switch memory usage increasing rapidly", "Resolved"),
    (6, 6, "Fan Failure", "Critical", "Cooling fan stopped on core switch", "Open"),
    (7, 1, "Power Fluctuating", "Medium", "UPS detected unstable input power", "In Progress"),
    (8, 2, "Bandwidth Peak", "Low", "Internet link at 90% utilization", "Resolved"),
    (9, 3, "Update Required", "Low", "New firmware available for Firewall", "Open"),
    (10, 4, "Latency Spike", "Medium", "Round-trip time exceeded 150ms", "Open"),
]
for a in alerts:
    try:
        execute_query(
            "INSERT INTO Alerts (DeviceID, AssignedTechID, AlertType, Severity, Message, Status, AlertTime) VALUES (?,?,?,?,?,?,GETDATE())",
            list(a)
        )
    except Exception as e:
        if 'duplicate' not in str(e).lower(): print(f"  Warning: {e}")
print(f"  Done - {len(alerts)} alerts")

# 4. Device_Status_History
print("4. Device_Status_History...")
status_changes = [
    (1, "Online", "Offline", "Unexpected power failure at Karachi DC", 3),
    (1, "Offline", "Online", "Power restored, device rebooted", 3),
    (3, "Online", "Maintenance", "Scheduled firmware upgrade", 1),
    (3, "Maintenance", "Online", "Firmware upgrade completed", 1),
    (5, "Online", "Offline", "Network interface failure", 5),
    (5, "Offline", "Degraded", "Partial recovery, backup link active", 5),
    (5, "Degraded", "Online", "Primary link restored", 5),
    (7, "Online", "Offline", "Cooling system failure in server room", 2),
    (7, "Offline", "Online", "HVAC repaired, server brought back up", 2),
    (9, "Online", "Maintenance", "Security patch deployment", 6),
    (10, "Online", "Offline", "DDoS attack detected, device isolated", 1),
    (10, "Offline", "Online", "Attack mitigated, device reconnected", 1),
]
for i, s in enumerate(status_changes):
    try:
        dt = datetime.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))
        execute_query(
            "INSERT INTO Device_Status_History (DeviceID, PreviousStatus, NewStatus, Reason, ChangedBy, ChangedAt) VALUES (?,?,?,?,?,?)",
            [s[0], s[1], s[2], s[3], s[4], dt.strftime('%Y-%m-%d %H:%M:%S')]
        )
    except Exception as e:
        print(f"  Warning: {e}")
print(f"  Done - {len(status_changes)} history entries")

# 5. Network_Links
print("5. Network_Links...")
links = [
    (1, 2, "Fiber", "10 Gbps", "1.2 ms", "0.01%", "Active"),
    (2, 3, "Fiber", "10 Gbps", "2.5 ms", "0.02%", "Active"),
    (1, 4, "Ethernet", "1 Gbps", "0.5 ms", "0.00%", "Active"),
    (3, 5, "VPN", "500 Mbps", "15.3 ms", "0.05%", "Active"),
    (5, 6, "Fiber", "10 Gbps", "3.1 ms", "0.01%", "Active"),
    (6, 7, "MPLS", "2 Gbps", "8.7 ms", "0.03%", "Active"),
    (7, 8, "Ethernet", "1 Gbps", "0.8 ms", "0.00%", "Active"),
    (8, 9, "Wireless", "300 Mbps", "5.2 ms", "0.12%", "Degraded"),
    (9, 10, "Fiber", "10 Gbps", "1.9 ms", "0.01%", "Active"),
    (10, 11, "VPN", "1 Gbps", "22.4 ms", "0.08%", "Active"),
    (11, 12, "Ethernet", "1 Gbps", "0.3 ms", "0.00%", "Active"),
    (1, 12, "MPLS", "5 Gbps", "4.6 ms", "0.02%", "Active"),
]
for l in links:
    try:
        execute_query(
            "INSERT INTO Network_Links (SourceDeviceID, TargetDeviceID, LinkType, Bandwidth, Latency, PacketLoss, Status, CreatedAt) VALUES (?,?,?,?,?,?,?,GETDATE())",
            list(l)
        )
    except Exception as e:
        print(f"  Warning: {e}")
print(f"  Done - {len(links)} network links")

# 6. Alert_Comments
print("6. Alert_Comments...")
comments = [
    (1, 1, "Initial investigation shows router interface went down due to power fluctuation.", "Note"),
    (1, 1, "Contacted site engineer, power supply being replaced.", "Update"),
    (1, 1, "Issue resolved. UPS installed as preventive measure.", "Resolution"),
    (2, 2, "High memory usage detected. Investigating running processes.", "Note"),
    (2, 2, "Found memory leak in monitoring agent v3.2. Restarted service.", "Update"),
    (3, 3, "Firewall rule misconfiguration causing intermittent drops.", "Note"),
    (3, 3, "Rules corrected and tested. Traffic flowing normally.", "Resolution"),
    (4, 4, "Bandwidth saturation during peak hours at ISB NOC.", "Note"),
    (5, 5, "CPU spike caused by backup job overlap. Rescheduling jobs.", "Update"),
    (5, 5, "Backup schedule adjusted. Monitoring for recurrence.", "Resolution"),
    (6, 6, "Temperature sensor triggered. Checking HVAC system.", "Note"),
    (7, 7, "Port flapping on Gi1/0/24. Cable replacement needed.", "Note"),
    (7, 7, "Cable replaced and port stable for 24 hours.", "Resolution"),
    (8, 8, "License expiry warning. Procurement notified.", "Note"),
    (9, 1, "Threat prevention license renewed. System updated.", "Update"),
]
for c in comments:
    try:
        dt = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        execute_query(
            "INSERT INTO Alert_Comments (AlertID, TechnicianID, Comment, CommentType, CommentedAt) VALUES (?,?,?,?,?)",
            [c[0], c[1], c[2], c[3], dt.strftime('%Y-%m-%d %H:%M:%S')]
        )
    except Exception as e:
        print(f"  Warning: {e}")
print(f"  Done - {len(comments)} comments")

# 6.1 Maintenance_Logs
print("6.1 Maintenance_Logs...")
maint_logs = [
    (1, 1, "Preventive", "Monthly hardware health check", "2024-05-01", "2024-05-01", 60, "Success"),
    (2, 2, "Upgrade", "Firmware update to v2.4.1", "2024-05-02", "2024-05-02", 120, "Success"),
    (3, 3, "Corrective", "Replaced faulty power adapter", "2024-05-03", "2024-05-03", 45, "Success"),
    (4, 4, "Preventive", "Cleaning server rack filters", "2024-05-04", "2024-05-04", 90, "Success"),
    (5, 5, "Emergency", "Fiber splice repair after construction damage", "2024-05-05", "2024-05-05", 240, "Partial"),
    (6, 6, "Upgrade", "Installed additional 16GB RAM", "2024-05-06", "2024-05-06", 30, "Success"),
    (7, 1, "Preventive", "Battery load test on UPS", "2024-05-07", "2024-05-07", 180, "Success"),
    (8, 2, "Corrective", "Resetting stuck management module", "2024-05-08", "2024-05-08", 15, "Success"),
    (9, 3, "Preventive", "Cable labeling and organization", "2024-05-09", "2024-05-09", 300, "Success"),
    (10, 4, "Emergency", "Restoring config from backup after crash", "2024-05-10", "2024-05-10", 60, "Success"),
]
for m in maint_logs:
    try:
        execute_query(
            "INSERT INTO Maintenance_Logs (DeviceID, TechnicianID, MaintenanceType, Description, ScheduledDate, CompletedDate, Duration_Minutes, Outcome, CreatedAt) VALUES (?,?,?,?,?,?,?,?,GETDATE())",
            list(m)
        )
    except Exception as e:
        if 'duplicate' not in str(e).lower(): print(f"  Warning: {e}")
print(f"  Done - {len(maint_logs)} maintenance logs")

# 7. Audit_Log
print("7. Audit_Log...")
audits = [
    (1, "INSERT", "Devices", 1, None, "KHI-CORE-RTR-01 created"),
    (1, "UPDATE", "Devices", 1, "Status: Offline", "Status: Online"),
    (2, "INSERT", "Alerts", 1, None, "High CPU usage alert created"),
    (3, "UPDATE", "Alerts", 1, "Status: Open", "Status: Assigned"),
    (1, "INSERT", "Maintenance_Logs", 1, None, "Hardware Upgrade scheduled"),
    (6, "UPDATE", "Technicians", 3, "Status: Available", "Status: Busy"),
    (2, "DELETE", "Alerts", 5, "Old resolved alert", None),
    (1, "UPDATE", "Locations", 2, "ContactPerson: null", "ContactPerson: Sara Ahmed"),
    (4, "INSERT", "Network_Links", 1, None, "Fiber link KHI-LHR created"),
    (1, "UPDATE", "SLA_Policies", 1, "ResponseTime: 30", "ResponseTime: 15"),
    (6, "INSERT", "Users", 7, None, "New technician Omar added"),
    (1, "UPDATE", "Devices", 5, "Status: Online", "Status: Maintenance"),
]
for a in audits:
    try:
        dt = datetime.now() - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23))
        execute_query(
            "INSERT INTO Audit_Log (UserID, Action, TableName, RecordID, OldValue, NewValue, Timestamp) VALUES (?,?,?,?,?,?,?)",
            [a[0], a[1], a[2], a[3], a[4], a[5], dt.strftime('%Y-%m-%d %H:%M:%S')]
        )
    except Exception as e:
        print(f"  Warning: {e}")
print(f"  Done - {len(audits)} audit entries")

print("\n=== ALL TABLES SEEDED ===")

# Verify counts
for t in ['Users','Vendors','Locations','Technicians','SLA_Policies','Devices',
          'Device_Status_History','Network_Links','Alerts','Alert_Comments',
          'Maintenance_Logs','Audit_Log']:
    try:
        r = execute_query(f"SELECT COUNT(*) as cnt FROM {t}")
        print(f"  {t}: {r[0]['cnt']} rows")
    except Exception as e:
        print(f"  {t}: ERROR - {e}")
