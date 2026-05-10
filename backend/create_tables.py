import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    import models # Ensure models are loaded
    db.create_all()
    print("Database tables created successfully at:")
    print(app.config['SQLALCHEMY_DATABASE_URI'])
