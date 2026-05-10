import app
from extensions import db
from models import Location, Technician, Vendor, MaintenanceLog, Incident, AuditLog, SLAPolicy

flask_app = app.create_app()
with flask_app.app_context():
    # Fix null is_deleted values
    for model in [Location, Technician, Vendor, MaintenanceLog, Incident, SLAPolicy]:
        records = model.query.all()
        count = 0
        for r in records:
            if getattr(r, 'is_deleted', None) is None:
                r.is_deleted = False
                count += 1
        db.session.commit()
        print(f"Updated {count} records in {model.__name__}")
    
    print("Done checking/fixing is_deleted values.")
