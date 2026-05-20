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

@db_objects_bp.route("/indexes", methods=["GET"])
@jwt_required()
@admin_required
def get_indexes():
    """List all indexes in the SQLite database"""
    query = "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
    result = db.session.execute(db.text(query)).fetchall()
    data = [{"index_name": r[0], "table_name": r[1]} for r in result]
    return jsonify({"success": True, "data": data})
