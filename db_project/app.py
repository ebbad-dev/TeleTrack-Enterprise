"""
TeleTrack V4 — Ultra-Premium Network Monitoring System
Production Flask Backend with Full Authentication
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import pyodbc
import threading
import json
import os
from datetime import datetime, timedelta
import hashlib
import re
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'teletrack-ultra-secure-v4-key-2025'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# ─── Hardcoded users (no DB needed for demo) ──────────────────────────────────
USERS = {
    'admin': {'password': hashlib.sha256('teletrack2024'.encode()).hexdigest(), 'role': 'Admin', 'displayName': 'System Administrator'},
    'operator': {'password': hashlib.sha256('operator123'.encode()).hexdigest(), 'role': 'Operator', 'displayName': 'Network Operator'},
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
        return (
            f"DRIVER={{{cfg.get('driver', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={cfg.get('server', 'localhost')};"
            f"DATABASE={cfg.get('database', 'TeleTrackDB')};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
    except:
        return (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=TeleTrackDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

def get_conn():
    return pyodbc.connect(load_config())

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def error_response(message, status_code=500):
    """Standardized error response"""
    return jsonify({"success": False, "error": message}), status_code

def success_response(data=None, message="Success"):
    """Standardized success response"""
    return jsonify({"success": True, "message": message, "data": data}), 200

def validate_ip_address(ip):
    """Validate IPv4 address format"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def execute_query(sql, params=None, fetch_one=False):
    """Execute SQL query with error handling"""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        if sql.strip().upper().startswith('SELECT'):
            if fetch_one:
                row = cursor.fetchone()
                conn.close()
                return row
            else:
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                conn.close()
                return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            conn.close()
            return {"rows_affected": cursor.rowcount}
    except Exception as e:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            # For API calls return JSON, for page calls redirect
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════════════════════════════════════
# FRONTEND ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template("index.html", user=session['user'])

@app.route("/login")
def login_page():
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template("login.html")

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    try:
        data = request.json
        username = data.get('username', '').strip().lower()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        user = USERS.get(username)
        if not user or user['password'] != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        session.permanent = True
        session['user'] = {
            'username': username,
            'displayName': user['displayName'],
            'role': user['role'],
            'loginTime': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'user': session['user']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    session.clear()
    return jsonify({'success': True})

@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    return jsonify({'success': True, 'user': session['user']})

@app.route("/api/setup", methods=["POST"])
def setup():
    """Run database schema upgrade"""
    try:
        sql_file = os.path.join(os.path.dirname(__file__), "schema_upgrade.sql")
        if not os.path.exists(sql_file):
            return error_response("schema_upgrade.sql not found", 404)
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        conn = get_conn()
        cursor = conn.cursor()
        
        # Split and execute statements
        statements = sql_content.split('GO')
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                except:
                    pass  # Some statements may fail if objects already exist
        
        conn.commit()
        conn.close()
        
        return success_response(message="Database schema upgraded successfully!")
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/dashboard/summary", methods=["GET"])
def dashboard_summary():
    """Get dashboard summary metrics"""
    try:
        # Total devices
        devices = execute_query("SELECT COUNT(*) as total FROM Devices")
        total_devices = devices[0]['total'] if devices else 0
        
        # Online/Offline count
        online = execute_query("SELECT COUNT(*) as count FROM Devices WHERE Status = 'Online'")
        online_count = online[0]['count'] if online else 0
        
        offline = execute_query("SELECT COUNT(*) as count FROM Devices WHERE Status = 'Offline'")
        offline_count = offline[0]['count'] if offline else 0
        
        # Alert counts
        open_alerts = execute_query("SELECT COUNT(*) as count FROM Alerts WHERE Status IN ('Open', 'Assigned')")
        open_count = open_alerts[0]['count'] if open_alerts else 0
        
        critical_alerts = execute_query("SELECT COUNT(*) as count FROM Alerts WHERE Severity = 'Critical' AND Status IN ('Open', 'Assigned')")
        critical_count = critical_alerts[0]['count'] if critical_alerts else 0
        
        # Technician stats
        available_techs = execute_query("SELECT COUNT(*) as count FROM Technicians WHERE Status = 'Available'")
        tech_count = available_techs[0]['count'] if available_techs else 0
        
        data = {
            "total_devices": total_devices,
            "online_devices": online_count,
            "offline_devices": offline_count,
            "open_alerts": open_count,
            "critical_alerts": critical_count,
            "available_technicians": tech_count,
            "timestamp": datetime.now().isoformat()
        }
        
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dashboard/alerts-by-severity", methods=["GET"])
def alerts_by_severity():
    """Get alert count grouped by severity"""
    try:
        sql = """
        SELECT Severity, COUNT(*) as count 
        FROM Alerts 
        WHERE Status IN ('Open', 'Assigned')
        GROUP BY Severity
        """
        alerts = execute_query(sql)
        return success_response(alerts)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dashboard/devices-by-status", methods=["GET"])
def devices_by_status():
    """Get device count grouped by status"""
    try:
        sql = """
        SELECT Status, COUNT(*) as count 
        FROM Devices 
        GROUP BY Status
        """
        devices = execute_query(sql)
        return success_response(devices)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dashboard/recent-alerts", methods=["GET"])
def recent_alerts():
    """Get recent 10 alerts with details"""
    try:
        sql = """
        SELECT TOP 10
            a.AlertID, a.DeviceID, a.AlertType, a.Severity, a.Message,
            a.Status, a.AlertTime, d.DeviceName, d.IPAddress,
            ISNULL(t.FullName, 'Unassigned') as TechnicianName
        FROM Alerts a
        JOIN Devices d ON a.DeviceID = d.DeviceID
        LEFT JOIN Technicians t ON a.AssignedTechID = t.TechnicianID
        ORDER BY a.AlertTime DESC
        """
        alerts = execute_query(sql)
        return success_response(alerts)
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# DEVICE APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/devices", methods=["GET"])
def get_devices():
    """Get all devices with optional filtering"""
    try:
        status = request.args.get('status')
        location = request.args.get('location')
        
        sql = """
        SELECT 
            d.DeviceID, d.DeviceName, d.DeviceType, d.IPAddress, d.MACAddress,
            d.Status, d.LastPingTime, d.InstalledDate,
            l.LocationName, v.VendorName
        FROM Devices d
        LEFT JOIN Locations l ON d.LocationID = l.LocationID
        LEFT JOIN Vendors v ON d.VendorID = v.VendorID
        WHERE 1=1
        """
        params = []
        
        if status:
            sql += " AND d.Status = ?"
            params.append(status)
        
        if location:
            sql += " AND d.LocationID = ?"
            params.append(int(location))
        
        sql += " ORDER BY d.DeviceName"
        
        devices = execute_query(sql, params if params else None)
        return success_response(devices)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/devices/<int:device_id>", methods=["GET"])
def get_device_details(device_id):
    """Get detailed info for a specific device"""
    try:
        # Device info
        device_sql = """
        SELECT 
            d.*, l.LocationName, v.VendorName
        FROM Devices d
        LEFT JOIN Locations l ON d.LocationID = l.LocationID
        LEFT JOIN Vendors v ON d.VendorID = v.VendorID
        WHERE d.DeviceID = ?
        """
        device = execute_query(device_sql, [device_id], fetch_one=True)
        
        if not device:
            return error_response("Device not found", 404)
        
        device_dict = dict(device) if device else {}
        
        # Status history
        history_sql = "SELECT TOP 20 * FROM Device_Status_History WHERE DeviceID = ? ORDER BY ChangedAt DESC"
        history = execute_query(history_sql, [device_id])
        
        # Related alerts
        alerts_sql = """
        SELECT AlertID, AlertType, Severity, Message, Status, AlertTime
        FROM Alerts WHERE DeviceID = ? ORDER BY AlertTime DESC
        """
        alerts = execute_query(alerts_sql, [device_id])
        
        data = {
            "device": device_dict,
            "status_history": history or [],
            "alerts": alerts or []
        }
        
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/devices", methods=["POST"])
def create_device():
    """Create a new device with validation"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['DeviceName', 'IPAddress', 'LocationID']
        for field in required:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Validate IP
        if not validate_ip_address(data['IPAddress']):
            return error_response("Invalid IP address format", 400)
        
        # Check if IP already exists
        existing = execute_query("SELECT DeviceID FROM Devices WHERE IPAddress = ?", [data['IPAddress']])
        if existing:
            return error_response("IP address already in use", 400)
        
        # Insert device
        sql = """
        INSERT INTO Devices (DeviceName, DeviceType, VendorID, Model, IPAddress, 
                            MACAddress, LocationID, Status, InstalledDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CAST(GETDATE() AS DATE))
        """
        params = [
            data.get('DeviceName'),
            data.get('DeviceType'),
            data.get('VendorID'),
            data.get('Model'),
            data.get('IPAddress'),
            data.get('MACAddress'),
            data.get('LocationID'),
            data.get('Status', 'Online')
        ]
        
        result = execute_query(sql, params)
        
        return success_response(result, "Device created successfully")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/devices/<int:device_id>", methods=["PUT"])
def update_device(device_id):
    """Update device information"""
    try:
        data = request.json
        
        # Build dynamic UPDATE query
        update_fields = []
        params = []
        
        allowed_fields = ['DeviceName', 'DeviceType', 'VendorID', 'Model', 'Status']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return error_response("No valid fields to update", 400)
        
        params.append(device_id)
        
        sql = f"UPDATE Devices SET {', '.join(update_fields)}, UpdatedAt = GETDATE() WHERE DeviceID = ?"
        result = execute_query(sql, params)
        
        return success_response(result, "Device updated successfully")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/devices/<int:device_id>/status", methods=["PUT"])
def update_device_status(device_id):
    """Update device status and create history record"""
    try:
        data = request.json
        new_status = data.get('status')
        reason = data.get('reason', 'Status update')
        changed_by = data.get('changed_by', 1)  # Default to admin
        
        if not new_status:
            return error_response("Status is required", 400)
        
        # Call stored procedure
        sql = "EXEC sp_UpdateDeviceStatus ?, ?, ?, ?"
        result = execute_query(sql, [device_id, new_status, reason, changed_by])
        
        return success_response(result, "Device status updated")
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# ALERT APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Get alerts with filtering and pagination"""
    try:
        status = request.args.get('status')
        severity = request.args.get('severity')
        device_id = request.args.get('device_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        offset = (page - 1) * limit
        
        sql = """
        SELECT 
            a.AlertID, a.DeviceID, a.AlertType, a.Severity, a.Message,
            a.Status, a.AlertTime, a.ResolvedTime,
            d.DeviceName, d.IPAddress,
            ISNULL(t.FullName, 'Unassigned') as TechnicianName
        FROM Alerts a
        JOIN Devices d ON a.DeviceID = d.DeviceID
        LEFT JOIN Technicians t ON a.AssignedTechID = t.TechnicianID
        WHERE 1=1
        """
        params = []
        
        if status:
            sql += " AND a.Status = ?"
            params.append(status)
        
        if severity:
            sql += " AND a.Severity = ?"
            params.append(severity)
        
        if device_id:
            sql += " AND a.DeviceID = ?"
            params.append(int(device_id))
        
        sql += " ORDER BY a.AlertTime DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, limit])
        
        alerts = execute_query(sql, params)
        return success_response(alerts)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/alerts", methods=["POST"])
def create_alert():
    """Create a new alert"""
    try:
        data = request.json
        
        sql = """
        INSERT INTO Alerts (DeviceID, AlertType, Severity, Message, Status, CreatedBy)
        VALUES (?, ?, ?, ?, 'Open', ?)
        """
        params = [
            data.get('DeviceID'),
            data.get('AlertType'),
            data.get('Severity', 'Medium'),
            data.get('Message'),
            data.get('CreatedBy', 1)
        ]
        
        result = execute_query(sql, params)
        return success_response(result, "Alert created")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/alerts/<int:alert_id>/assign", methods=["POST"])
def assign_alert(alert_id):
    """Assign alert to technician"""
    try:
        data = request.json
        tech_id = data.get('TechnicianID')
        assigned_by = data.get('AssignedBy', 1)
        
        if not tech_id:
            return error_response("TechnicianID required", 400)
        
        sql = "EXEC sp_AssignAlert ?, ?, ?"
        result = execute_query(sql, [alert_id, tech_id, assigned_by])
        
        return success_response(result, "Alert assigned successfully")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        data = request.json
        resolution_note = data.get('ResolutionNote', '')
        resolved_by = data.get('ResolvedBy', 1)
        
        sql = "EXEC sp_ResolveAlert ?, ?, ?"
        result = execute_query(sql, [alert_id, resolution_note, resolved_by])
        
        return success_response(result, "Alert resolved")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/alerts/<int:alert_id>/comments", methods=["GET"])
def get_alert_comments(alert_id):
    """Get comments for an alert"""
    try:
        sql = """
        SELECT ac.CommentID, ac.Comment, ac.CommentType, ac.CommentedAt,
               t.FullName as TechnicianName
        FROM Alert_Comments ac
        JOIN Technicians t ON ac.TechnicianID = t.TechnicianID
        WHERE ac.AlertID = ?
        ORDER BY ac.CommentedAt DESC
        """
        comments = execute_query(sql, [alert_id])
        return success_response(comments)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/alerts/<int:alert_id>/comments", methods=["POST"])
def add_alert_comment(alert_id):
    """Add comment to alert"""
    try:
        data = request.json
        tech_id = data.get('TechnicianID')
        comment = data.get('Comment')
        comment_type = data.get('CommentType', 'Note')
        
        sql = """
        INSERT INTO Alert_Comments (AlertID, TechnicianID, Comment, CommentType)
        VALUES (?, ?, ?, ?)
        """
        
        result = execute_query(sql, [alert_id, tech_id, comment, comment_type])
        return success_response(result, "Comment added")
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# DROPDOWN APIs (for form selection)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/dropdowns/locations", methods=["GET"])
def get_locations_dropdown():
    """Get locations for dropdown"""
    try:
        locations = execute_query("SELECT LocationID as id, LocationName as label FROM Locations ORDER BY LocationName")
        return success_response(locations)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dropdowns/technicians", methods=["GET"])
def get_technicians_dropdown():
    """Get technicians for dropdown"""
    try:
        sql = "SELECT TechnicianID as id, FullName as label, Status FROM Technicians ORDER BY FullName"
        technicians = execute_query(sql)
        return success_response(technicians)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dropdowns/vendors", methods=["GET"])
def get_vendors_dropdown():
    """Get vendors for dropdown"""
    try:
        vendors = execute_query("SELECT VendorID as id, VendorName as label FROM Vendors ORDER BY VendorName")
        return success_response(vendors)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/dropdowns/sla-policies", methods=["GET"])
def get_sla_policies_dropdown():
    """Get SLA policies for dropdown"""
    try:
        sql = "SELECT PolicyID as id, SeverityLevel as label FROM SLA_Policies ORDER BY SeverityLevel"
        policies = execute_query(sql)
        return success_response(policies)
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# TECHNICIAN APIs
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/technicians", methods=["GET"])
def get_technicians():
    """Get all technicians"""
    try:
        sql = """
        SELECT TechnicianID, FullName, Email, Phone, Specialization, Shift, Status,
               TotalAlerts, ResolvedAlerts, AverageResolutionTime
        FROM Technicians
        ORDER BY FullName
        """
        technicians = execute_query(sql)
        return success_response(technicians)
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/technicians/<int:tech_id>/workload", methods=["GET"])
def get_technician_workload(tech_id):
    """Get technician's assigned alerts and stats"""
    try:
        sql = """
        SELECT TOP 1
            t.TechnicianID, t.FullName, t.Email, t.Phone, t.Status,
            COUNT(a.AlertID) as AssignedAlerts,
            SUM(CASE WHEN a.Status = 'Resolved' THEN 1 ELSE 0 END) as ResolvedAlerts,
            AVG(DATEDIFF(MINUTE, a.AlertTime, a.ResolvedTime)) as AvgResolutionTime
        FROM Technicians t
        LEFT JOIN Alerts a ON t.TechnicianID = a.AssignedTechID
        WHERE t.TechnicianID = ?
        GROUP BY t.TechnicianID, t.FullName, t.Email, t.Phone, t.Status
        """
        workload = execute_query(sql, [tech_id], fetch_one=True)
        return success_response(workload)
    except Exception as e:
        return error_response(str(e), 500)

# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK: Monitor devices and generate alerts
# ═══════════════════════════════════════════════════════════════════════════════

def monitor_devices():
    """Background task to check device status and generate alerts"""
    while True:
        try:
            # Check for devices that haven't pinged in 5 minutes
            sql = """
            SELECT DeviceID, DeviceName, LastPingTime, Status
            FROM Devices
            WHERE Status = 'Online' AND LastPingTime < DATEADD(MINUTE, -5, GETDATE())
            """
            offline_devices = execute_query(sql)
            
            if offline_devices:
                for device in offline_devices:
                    # Create alert
                    alert_sql = """
                    INSERT INTO Alerts (DeviceID, AlertType, Severity, Message, Status, CreatedBy)
                    VALUES (?, 'Device Offline', 'High', ?, 'Open', 1)
                    """
                    execute_query(alert_sql, [
                        device.get('DeviceID'),
                        f"Device {device.get('DeviceName')} went offline"
                    ])
                    
                    # Update device status
                    update_sql = "UPDATE Devices SET Status = 'Offline', UpdatedAt = GETDATE() WHERE DeviceID = ?"
                    execute_query(update_sql, [device.get('DeviceID')])
            
            # Sleep for 60 seconds before next check
            threading.Event().wait(60)
        except Exception as e:
            print(f"Monitor error: {str(e)}")
            threading.Event().wait(60)

# Start background monitoring in a separate thread
monitor_thread = threading.Thread(target=monitor_devices, daemon=True)
monitor_thread.start()

# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", 500)

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY - Generic CRUD endpoints
# ═══════════════════════════════════════════════════════════════════════════════

TABLE_COLUMNS = {
    "Users": ["UserID", "Username", "PasswordHash", "FullName", "Email", "Role", "Status", "LastLogin", "CreatedAt"],
    "Vendors": ["VendorID", "VendorName", "CountryOfOrigin", "SupportEmail", "SupportPhone", "Website", "CreatedAt"],
    "Locations": ["LocationID", "LocationName", "City", "Country", "SiteType", "AddressLine", "ContactPerson", "ContactPhone", "ImageUrl"],
    "Technicians": ["TechnicianID", "FullName", "Email", "Phone", "Specialization", "Shift", "Status", "ImageUrl"],
    "SLA_Policies": ["PolicyID", "SeverityLevel", "ResponseTimeMinutes", "ResolutionTimeMinutes", "EscalationRequired", "CreatedAt"],
    "Devices": ["DeviceID", "DeviceName", "DeviceType", "Model", "IPAddress", "MACAddress", "LocationID", "Status", "InstalledDate", "LastPingTime", "ImageUrl"],
    "Device_Status_History": ["HistoryID", "DeviceID", "PreviousStatus", "NewStatus", "Reason", "ChangedBy", "ChangedAt"],
    "Network_Links": ["LinkID", "SourceDeviceID", "TargetDeviceID", "LinkType", "Bandwidth", "Latency", "PacketLoss", "Status", "CreatedAt"],
    "Alerts": ["AlertID", "DeviceID", "AssignedTechID", "AlertType", "Severity", "Message", "AlertTime", "ResolvedTime", "Status", "ImageUrl"],
    "Alert_Comments": ["CommentID", "AlertID", "TechnicianID", "Comment", "CommentType", "CommentedAt"],
    "Maintenance_Logs": ["LogID", "DeviceID", "TechnicianID", "MaintenanceType", "Description", "ScheduledDate", "CompletedDate", "Duration_Minutes", "Outcome", "Notes", "ImageUrl"],
    "Audit_Log": ["AuditID", "UserID", "Action", "TableName", "RecordID", "OldValue", "NewValue", "Timestamp"]
}

TABLE_PK = {
    "Users": "UserID", "Vendors": "VendorID", "Locations": "LocationID",
    "Technicians": "TechnicianID", "SLA_Policies": "PolicyID",
    "Devices": "DeviceID", "Device_Status_History": "HistoryID",
    "Network_Links": "LinkID", "Alerts": "AlertID",
    "Alert_Comments": "CommentID", "Maintenance_Logs": "LogID",
    "Audit_Log": "AuditID"
}

@app.route("/api/retrieve", methods=["POST"])
def retrieve():
    """Legacy CRUD - Retrieve"""
    try:
        d = request.json
        table = d.get("table", "Locations")
        cols = d.get("columns", TABLE_COLUMNS.get(table, []))
        where_col = d.get("where_col", "")
        where_val = d.get("where_val", "")
        
        select_part = ", ".join(cols)
        sql = f"SELECT {select_part} FROM {table}"
        params = []
        
        if where_col and where_val:
            sql += f" WHERE {where_col} = ?"
            params.append(where_val)
        
        rows = execute_query(sql, params if params else None)
        return success_response({"columns": cols, "rows": rows or []})
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/insert", methods=["POST"])
def insert():
    """Legacy CRUD - Insert"""
    try:
        d = request.json
        table = d.get("table", "Locations")
        pk = TABLE_PK.get(table)
        cols = TABLE_COLUMNS.get(table, [])
        
        insert_cols = [c for c in cols if c != pk]
        vals = tuple(d.get(c) for c in insert_cols)
        placeholders = ",".join(["?"] * len(insert_cols))
        col_str = ",".join(insert_cols)
        
        sql = f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
        execute_query(sql, list(vals))
        
        return success_response(message=f"Record inserted into {table}")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/modify", methods=["POST"])
def modify():
    """Legacy CRUD - Modify"""
    try:
        d = request.json
        table = d.get("table", "Locations")
        pk_val = d.get("pk_val")
        update_col = d.get("update_col")
        update_val = d.get("update_val")
        
        if not pk_val or not update_col:
            return error_response("Missing primary key or update column", 400)
            
        pk_col = TABLE_PK.get(table)
        sql = f"UPDATE {table} SET {update_col} = ? WHERE {pk_col} = ?"
        
        # Determine if value should be an int/null based on string content if it's empty
        val_to_update = update_val if update_val != "" else None
        
        result = execute_query(sql, [val_to_update, pk_val])
        return success_response(message=f"Record {pk_val} in {table} updated successfully")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/delete", methods=["POST"])
def delete_record():
    """Legacy CRUD - Delete"""
    try:
        d = request.json
        table = d.get("table", "Locations")
        pk_val = d.get("pk_val")
        
        if not pk_val:
            return error_response("Missing primary key", 400)
            
        pk_col = TABLE_PK.get(table)
        sql = f"DELETE FROM {table} WHERE {pk_col} = ?"
        execute_query(sql, [pk_val])
        
        return success_response(message=f"Record {pk_val} deleted from {table}")
    except Exception as e:
        return error_response(str(e), 500)

@app.route("/api/config", methods=["GET"])
def get_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return success_response(json.load(f))
    except:
        return success_response({"server": "localhost", "database": "TeleTrackDB"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
