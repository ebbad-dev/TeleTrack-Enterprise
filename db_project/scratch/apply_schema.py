from app import execute_query

tables = ['Locations', 'Technicians', 'Devices', 'Alerts', 'Maintenance_Logs']

print("=== APPLYING SCHEMA UPDATES ===")
for t in tables:
    try:
        print(f"Adding ImageUrl to {t}...")
        execute_query(f"ALTER TABLE {t} ADD ImageUrl VARCHAR(500)")
        print(f"  Success")
    except Exception as e:
        if 'already' in str(e).lower() or 'duplicate' in str(e).lower():
            print(f"  Already exists")
        else:
            print(f"  Error: {e}")

print("\nDone.")
