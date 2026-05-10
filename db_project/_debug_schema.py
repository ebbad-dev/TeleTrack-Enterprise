from app import execute_query

# Check Alerts table columns
try:
    cols = execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Alerts' ORDER BY ORDINAL_POSITION")
    print("Alerts columns:")
    for c in cols:
        print(f"  - {c['COLUMN_NAME']}")
except Exception as e:
    print(f"Error: {e}")

# Check Alerts row count  
try:
    r = execute_query("SELECT COUNT(*) as cnt FROM Alerts")
    print(f"\nAlerts rows: {r[0]['cnt']}")
except Exception as e:
    print(f"Count error: {e}")

# Check Technicians too
try:
    r = execute_query("SELECT COUNT(*) as cnt FROM Technicians")
    print(f"Technicians rows: {r[0]['cnt']}")
    cols = execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Technicians' ORDER BY ORDINAL_POSITION")
    print("Technicians columns:")
    for c in cols:
        print(f"  - {c['COLUMN_NAME']}")
except Exception as e:
    print(f"Technicians error: {e}")
