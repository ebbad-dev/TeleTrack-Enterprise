"""
TeleTrack Enterprise — Database Reset & Seed
Drops all tables, recreates them, and runs full seed.
Usage: python reset_and_seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

def reset_database():
    app = create_app()
    with app.app_context():
        print("\n[INFO] DROPPING ALL TABLES...")
        db.drop_all()
        print("[SUCCESS] All tables dropped.\n")

        print("[INFO] CREATING ALL TABLES...")
        db.create_all()
        print("[SUCCESS] All tables created.\n")

        print("[INFO] SEEDING DATABASE...")
        from seeds.seed_data import seed_all
        seed_all()

        print("[INFO] CREATING DATABASE VIEWS AND TRIGGERS...")
        create_database_objects()

        print("\n[COMPLETE] DATABASE RESET COMPLETE!")
        print("   Login: admin / admin123\n")


def create_database_objects():
    """Create advanced database objects (views, triggers)."""
    # Active devices view
    db.session.execute(db.text('''
    CREATE VIEW IF NOT EXISTS view_active_devices AS
    SELECT * FROM devices WHERE status = 'online' AND is_deleted = 0;
    '''))
    
    # Critical alerts view
    db.session.execute(db.text('''
    CREATE VIEW IF NOT EXISTS view_critical_alerts AS
    SELECT * FROM alerts WHERE severity = 'critical' AND status IN ('open', 'assigned') AND is_deleted = 0;
    '''))

    # Open incidents view
    db.session.execute(db.text('''
    CREATE VIEW IF NOT EXISTS view_open_incidents AS
    SELECT * FROM incidents WHERE status IN ('open', 'acknowledged', 'investigating') AND is_deleted = 0;
    '''))
    
    # Triggers for audit logs
    # Triggers on device table
    db.session.execute(db.text('''
    CREATE TRIGGER IF NOT EXISTS trg_audit_device_insert
    AFTER INSERT ON devices
    BEGIN
        INSERT INTO audit_logs (user_id, action, resource, timestamp)
        VALUES (1, 'DEVICE_CREATE', 'devices', CURRENT_TIMESTAMP);
    END;
    '''))

    db.session.execute(db.text('''
    CREATE TRIGGER IF NOT EXISTS trg_device_status_change
    AFTER UPDATE OF status ON devices
    WHEN old.status != new.status
    BEGIN
        INSERT INTO device_status_history (device_id, previous_status, new_status, reason, changed_at)
        VALUES (new.id, old.status, new.status, 'Status changed via system trigger', CURRENT_TIMESTAMP);
    END;
    '''))
    
    # Create Indexes
    db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);'))
    db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);'))
    db.session.execute(db.text('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);'))
    
    db.session.commit()
    print("   Database views, triggers, and indexes created successfully.")

if __name__ == "__main__":
    reset_database()
