"""
TeleTrack Enterprise — Database Objects Routes
Exposes Data from Views, Triggers, and Procedures.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from auth.decorators import admin_required

db_objects_bp = Blueprint("db_objects", __name__, url_prefix="/api/database")

@db_objects_bp.route("/views/active-devices", methods=["GET"])
@jwt_required()
@admin_required
def get_view_active_devices():
    """Fetch from SQL View: view_active_devices"""
    result = db.session.execute(db.text("SELECT * FROM view_active_devices")).fetchall()
    data = [dict(r._mapping) for r in result]
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/views/critical-alerts", methods=["GET"])
@jwt_required()
@admin_required
def get_view_critical_alerts():
    """Fetch from SQL View: view_critical_alerts"""
    result = db.session.execute(db.text("SELECT * FROM view_critical_alerts")).fetchall()
    data = [dict(r._mapping) for r in result]
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/views/open-incidents", methods=["GET"])
@jwt_required()
@admin_required
def get_view_open_incidents():
    """Fetch from SQL View: view_open_incidents"""
    result = db.session.execute(db.text("SELECT * FROM view_open_incidents")).fetchall()
    data = [dict(r._mapping) for r in result]
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/triggers/status-history", methods=["GET"])
@jwt_required()
@admin_required
def get_trigger_status_history():
    """Fetch history populated by trg_device_status_change"""
    result = db.session.execute(db.text("SELECT * FROM device_status_history ORDER BY changed_at DESC LIMIT 50")).fetchall()
    data = [dict(r._mapping) for r in result]
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/procedures/network-stats", methods=["GET"])
@jwt_required()
@admin_required
def get_procedure_network_stats():
    """
    Mock Stored Procedure: Calculate network-wide uptime and load averages.
    In a real SQL Server/Postgres this would be a CALL sp_network_stats()
    Here we use a complex query to simulate it.
    """
    query = """
    SELECT 
        COUNT(id) as total_devices,
        SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online_devices,
        AVG(cpu_usage) as avg_cpu,
        AVG(memory_usage) as avg_memory
    FROM devices
    WHERE is_deleted = 0
    """
    result = db.session.execute(db.text(query)).fetchone()
    data = dict(result._mapping) if result else {}
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/procedures/predictive-analytics", methods=["GET"])
@jwt_required()
@admin_required
def get_predictive_analytics():
    """
    Simulated AI/Predictive Analytics Stored Procedure.
    Analyzes Alerts and Devices to predict imminent failures.
    """
    query = """
    SELECT 
        d.id as device_id,
        d.device_name,
        d.device_type,
        d.status,
        COUNT(a.id) as recent_alerts,
        MAX(a.created_at) as last_alert_time,
        (COUNT(a.id) * 15 + CASE WHEN d.status = 'degraded' THEN 30 ELSE 0 END) as failure_probability
    FROM devices d
    LEFT JOIN alerts a ON d.id = a.device_id AND a.status != 'resolved'
    WHERE d.is_deleted = 0
    GROUP BY d.id
    HAVING failure_probability > 0
    ORDER BY failure_probability DESC
    LIMIT 10
    """
    result = db.session.execute(db.text(query)).fetchall()
    data = [dict(r._mapping) for r in result]
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/indexes", methods=["GET"])
@jwt_required()
@admin_required
def get_indexes():
    """List all indexes in the SQLite database"""
    query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    result = db.session.execute(db.text(query)).fetchall()
    
    # Extract column name from sql
    data = []
    for r in result:
        col = ""
        if r[2]:
            import re
            m = re.search(r'\((.*?)\)', r[2])
            if m:
                col = m.group(1).strip()
        data.append({"index_name": r[0], "table_name": r[1], "column_name": col})
    return jsonify({"success": True, "data": data})

@db_objects_bp.route("/indexes/<table_name>/<column_name>", methods=["GET"])
@jwt_required()
@admin_required
def get_index_sample(table_name, column_name):
    """Fetch sample data ordered by the index column to demonstrate indexing"""
    # Validate table_name against sqlite_master to prevent SQL injection
    check_table = db.session.execute(
        db.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
        {"table_name": table_name}
    ).fetchone()
    
    if not check_table:
        return jsonify({"success": False, "error": "Invalid table"}), 400
        
    # Column name is sanitized by virtue of being parsed from an index
    # But just in case, removing anything non-alphanumeric/underscore
    import re
    column_name_clean = re.sub(r'[^a-zA-Z0-9_]', '', column_name)
    
    query = f"SELECT * FROM {table_name} ORDER BY {column_name_clean} LIMIT 50"
    try:
        result = db.session.execute(db.text(query)).fetchall()
        data = [dict(r._mapping) for r in result]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
@db_objects_bp.route("/time-travel", methods=["GET"])
@jwt_required()
@admin_required
def get_time_travel_snapshot():
    """
    Simulated 'Time-Travel' Auditing.
    Returns the network's state at a given timestamp by rolling back the `device_status_history` log.
    Expects ?timestamp=YYYY-MM-DDTHH:MM:SS
    """
    from flask import request
    target_time = request.args.get("timestamp")
    if not target_time:
        return jsonify({"success": False, "error": "Missing timestamp"}), 400

    # Complex Query:
    # Get current devices. If a device has a history entry AFTER the target_time, 
    # its status at target_time was the `previous_status` of the FIRST change that occurred AFTER target_time.
    # Otherwise, its status hasn't changed since target_time, so use current status.
    query = """
    WITH FirstChangeAfter AS (
        SELECT device_id, previous_status,
               ROW_NUMBER() OVER(PARTITION BY device_id ORDER BY changed_at ASC) as rn
        FROM device_status_history
        WHERE changed_at > :target_time
    )
    SELECT 
        d.id as device_id,
        d.device_name,
        d.device_type,
        COALESCE(fc.previous_status, d.status) as historical_status,
        d.status as current_status
    FROM devices d
    LEFT JOIN FirstChangeAfter fc ON d.id = fc.device_id AND fc.rn = 1
    WHERE d.is_deleted = 0
    ORDER BY d.id
    """
    try:
        result = db.session.execute(db.text(query), {"target_time": target_time}).fetchall()
        data = [dict(r._mapping) for r in result]
        return jsonify({"success": True, "data": data, "snapshot_time": target_time})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
