import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app import create_app
from models.user import User
from extensions import db

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if user:
        user.status = "active"
        user.is_deleted = False
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        print("SUCCESS: Admin account is now ACTIVE and UNLOCKED.")
    else:
        print("ERROR: Admin user not found.")
