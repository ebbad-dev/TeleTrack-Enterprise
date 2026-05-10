"""Quick test for all core API endpoints."""
import urllib.request
import json

BASE = "http://127.0.0.1:5000"

def api(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": json.loads(e.read())}

# 1. Health check
print("1. Health check:")
print(f"   {api('GET', '/api/health')}")

# 2. Login
print("\n2. Login:")
login_res = api("POST", "/api/auth/login", {"username": "admin", "password": "TeleTrack@2026"})
print(f"   Success: {login_res.get('success')}")
print(f"   User: {login_res.get('user', {}).get('full_name')}")
token = login_res.get("access_token", "")
print(f"   Token: {token[:40]}...")

# 3. Get current user
print("\n3. Current user (/api/auth/me):")
me = api("GET", "/api/auth/me", token=token)
print(f"   {me}")

# 4. Dashboard summary
print("\n4. Dashboard summary:")
dash = api("GET", "/api/dashboard/summary", token=token)
print(f"   {json.dumps(dash.get('data', dash), indent=2)}")

# 5. Devices list
print("\n5. Devices:")
devs = api("GET", "/api/devices", token=token)
if devs.get("data"):
    print(f"   Total: {devs['meta']['total']} devices")
    for d in devs["data"][:3]:
        print(f"   - {d['device_name']} ({d['ip_address']}) [{d['status']}]")
else:
    print(f"   {devs}")

# 6. Alerts list
print("\n6. Alerts:")
alerts = api("GET", "/api/alerts", token=token)
if alerts.get("data"):
    print(f"   Total: {alerts['meta']['total']} alerts")
    for a in alerts["data"][:3]:
        print(f"   - [{a['severity']}] {a['alert_type']} - {a['status']}")
else:
    print(f"   {alerts}")

# 7. Global search
print("\n7. Global search (query='KHI'):")
search = api("GET", "/api/search?q=KHI", token=token)
print(f"   {search.get('message', search)}")

# 8. Dropdowns
print("\n8. Dropdown - locations:")
locs = api("GET", "/api/dropdowns/locations", token=token)
if locs.get("data"):
    print(f"   {len(locs['data'])} locations loaded")

print("\n--- ALL TESTS COMPLETE ---")
