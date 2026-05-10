import os
import sys
from werkzeug.security import check_password_hash
import bcrypt

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app import create_app
from models.user import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username="admin").first()
    if not user:
        print("USER NOT FOUND")
    else:
        print(f"User: {user.username}")
        print(f"Email: {user.email}")
        print(f"Hash: {user.password_hash}")
        
        # Test Bcrypt (what we want)
        try:
            is_bcrypt = bcrypt.checkpw("admin123".encode('utf-8'), user.password_hash.encode('utf-8'))
            print(f"Bcrypt Match (admin123): {is_bcrypt}")
        except Exception as e:
            print(f"Bcrypt Check Failed: {e}")
            
        # Test Werkzeug (what we might have had)
        is_werkzeug = check_password_hash(user.password_hash, "admin123")
        print(f"Werkzeug Match (admin123): {is_werkzeug}")
