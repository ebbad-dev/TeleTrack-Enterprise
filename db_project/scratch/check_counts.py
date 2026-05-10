from app import execute_query

tables = [
    'Alert_Comments', 'Alerts', 'Audit_Log', 'Device_Status_History',
    'Devices', 'Locations', 'Maintenance_Logs', 'Network_Links',
    'SLA_Policies', 'Technicians', 'Users', 'Vendors'
]

print('=== TABLE COUNTS ===')
for t in tables:
    try:
        r = execute_query(f"SELECT COUNT(*) as cnt FROM {t}")
        print(f"{t}: {r[0]['cnt']}")
    except Exception as e:
        print(f"{t}: ERROR - {e}")
