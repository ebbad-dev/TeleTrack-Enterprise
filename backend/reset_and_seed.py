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
        print("\n⚠️  DROPPING ALL TABLES...")
        db.drop_all()
        print("✅ All tables dropped.\n")

        print("🔧 CREATING ALL TABLES...")
        db.create_all()
        print("✅ All tables created.\n")

        print("🌱 SEEDING DATABASE...")
        from seeds.seed_data import seed_all
        seed_all()

        print("\n🚀 DATABASE RESET COMPLETE!")
        print("   Login: admin / admin123\n")


if __name__ == "__main__":
    reset_database()
