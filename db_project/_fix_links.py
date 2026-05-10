from app import execute_query

# Network_Links - Bandwidth/Latency/PacketLoss are FLOAT columns
links = [
    (1, 2, "Fiber", 10000, 1.2, 0.01, "Active"),
    (2, 3, "Fiber", 10000, 2.5, 0.02, "Active"),
    (1, 4, "Ethernet", 1000, 0.5, 0.00, "Active"),
    (3, 5, "VPN", 500, 15.3, 0.05, "Active"),
    (5, 6, "Fiber", 10000, 3.1, 0.01, "Active"),
    (6, 7, "MPLS", 2000, 8.7, 0.03, "Active"),
    (7, 8, "Ethernet", 1000, 0.8, 0.00, "Active"),
    (8, 9, "Wireless", 300, 5.2, 0.12, "Degraded"),
    (9, 10, "Fiber", 10000, 1.9, 0.01, "Active"),
    (10, 11, "VPN", 1000, 22.4, 0.08, "Active"),
    (11, 12, "Ethernet", 1000, 0.3, 0.00, "Active"),
    (1, 12, "MPLS", 5000, 4.6, 0.02, "Active"),
]

ok = 0
for i, l in enumerate(links):
    try:
        result = execute_query(
            "INSERT INTO Network_Links (SourceDeviceID, TargetDeviceID, LinkType, Bandwidth, Latency, PacketLoss, Status, CreatedAt) VALUES (?,?,?,?,?,?,?,GETDATE())",
            list(l)
        )
        if result is not None:
            ok += 1
            print(f"  Link {i+1}: OK")
        else:
            print(f"  Link {i+1}: returned None (silent error)")
    except Exception as e:
        print(f"  Link {i+1}: EXCEPTION - {e}")

r = execute_query("SELECT COUNT(*) as cnt FROM Network_Links")
print(f"\nTotal: {r[0]['cnt']} rows ({ok} inserted this run)")
