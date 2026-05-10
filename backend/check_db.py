import app
from extensions import db
from models import Location, Technician, Vendor, Role, User, Permission

flask_app = app.create_app()
with flask_app.app_context():
    print(f"Locations: {Location.query.count()}")
    print(f"Technicians: {Technician.query.count()}")
    print(f"Vendors: {Vendor.query.count()}")
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("Admin roles:", [r.name for r in admin_user.roles])
        for r in admin_user.roles:
            print(f"Role {r.name} permissions: {[p.name for p in r.permissions]}")
