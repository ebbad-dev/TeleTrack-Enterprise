from app import execute_query

tables = execute_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")
print('=== EXISTING TABLES ===')
for t in tables:
    print(t['TABLE_NAME'])
print(f'\nTotal: {len(tables)} tables')
