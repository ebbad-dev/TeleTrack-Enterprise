from app import execute_query

# Unique images per row using Unsplash source with different search terms
# Each row gets a distinct image via unique sig parameter

image_sets = {
    'Locations': [
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&q=80',  # Server room
        'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&q=80',  # Office building
        'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80',  # Skyscraper
        'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&q=80',  # Circuit board
        'https://images.unsplash.com/photo-1573164713988-8665fc963095?w=400&q=80',  # Data center
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80',  # Earth from space
        'https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=400&q=80',  # Modern office
        'https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=400&q=80',  # Corporate
        'https://images.unsplash.com/photo-1577760258779-e787a1733016?w=400&q=80',  # Factory
    ],
    'Devices': [
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&q=80',  # Router
        'https://images.unsplash.com/photo-1606765962248-7ff407b51667?w=400&q=80',  # Network switch
        'https://images.unsplash.com/photo-1563770660941-20978e870e26?w=400&q=80',  # Server rack
        'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400&q=80',  # Computer setup
        'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&q=80',  # Tech hardware
        'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&q=80',  # Server
        'https://images.unsplash.com/photo-1597852074816-d933c7d2b988?w=400&q=80',  # Cables
        'https://images.unsplash.com/photo-1610563166150-b34df4f3bcd6?w=400&q=80',  # Monitor
        'https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=400&q=80',  # Laptop
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&q=80',  # Tech abstract
        'https://images.unsplash.com/photo-1580584126903-c17d41830f0b?w=400&q=80',  # Hardware
        'https://images.unsplash.com/photo-1517430816045-df4b7de11d1d?w=400&q=80',  # Computer
    ],
    'Technicians': [
        'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&q=80',  # Business man
        'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=400&q=80',  # Business woman
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',  # Portrait male
        'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&q=80',  # Portrait female
        'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80',  # Professional
        'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80',  # Tech woman
        'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=80',  # Man face
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&q=80',  # Woman face
    ],
    'Alerts': [
        'https://images.unsplash.com/photo-1555861496-faa3aebc95ee?w=400&q=80',  # Code screen
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&q=80',  # Matrix
        'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=400&q=80',  # Warning
        'https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=400&q=80',  # Security
        'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400&q=80',  # Hacker
        'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=400&q=80',  # Code
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400&q=80',  # Cyber
        'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=400&q=80',  # Laptop code
        'https://images.unsplash.com/photo-1562813733-b31f71025d54?w=400&q=80',  # Dashboard
        'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=400&q=80',  # Office
    ],
    'Maintenance_Logs': [
        'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400&q=80',  # Engineer
        'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=400&q=80',  # Repair
        'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400&q=80',  # Lab work
        'https://images.unsplash.com/photo-1590959651373-a3db0f38a961?w=400&q=80',  # Tools
        'https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=400&q=80',  # Maintenance
        'https://images.unsplash.com/photo-1504384764586-bb4cdc1707b0?w=400&q=80',  # Working
        'https://images.unsplash.com/photo-1517420704952-d9f39e95b43e?w=400&q=80',  # Server work
        'https://images.unsplash.com/photo-1580894894513-541e068a3e2b?w=400&q=80',  # Fixing
        'https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=400&q=80',  # Teamwork
        'https://images.unsplash.com/photo-1581092335397-9583eb92d232?w=400&q=80',  # Tech repair
    ],
}

for table, imgs in image_sets.items():
    # Get primary key column name
    pk_map = {
        'Locations': 'LocationID', 'Devices': 'DeviceID',
        'Technicians': 'TechnicianID', 'Alerts': 'AlertID',
        'Maintenance_Logs': 'LogID'
    }
    pk = pk_map[table]

    # Get all rows
    rows = execute_query(f"SELECT {pk} FROM {table} ORDER BY {pk}")
    if not rows:
        print(f"  {table}: No rows found")
        continue

    count = 0
    for i, row in enumerate(rows):
        img_url = imgs[i % len(imgs)]
        result = execute_query(f"UPDATE {table} SET ImageUrl = ? WHERE {pk} = ?", [img_url, row[pk]])
        count += 1

    print(f"  {table}: Updated {count} rows with unique images")

print("\nDone! All tables now have unique images per row.")
