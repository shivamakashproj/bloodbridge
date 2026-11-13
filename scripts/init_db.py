"""
BloodBridge Database Initialization & Administrative Seed Script
Run this script to automatically create MySQL tables and seed the initial super-admin account.
Usage: python scripts/init_db.py
"""

import sys
import os

# Add parent directory to path so models and app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Donor, Campaign, BloodRequest


def init_database():
    print("==================================================")
    print("[*] Initializing BloodBridge Production Database...")
    print("==================================================")

    with app.app_context():
        # Create all tables
        db.create_all()
        print("[OK] Database tables verified/created successfully.")

        # Create admin only if credentials are provided via environment variables
        admin_user = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_pass = os.environ.get('ADMIN_PASSWORD')

        if admin_user and admin_pass:
            admin = User.query.filter_by(username=admin_user).first()
            if not admin:
                admin = User(
                    username=admin_user,
                    email=admin_email or f"{admin_user}@bloodbridge.in",
                    password_hash=generate_password_hash(admin_pass),
                    role='admin',
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print(f"[+] Admin account created for '{admin_user}' via environment variables.")
            else:
                print(f"[i] Admin '{admin_user}' already exists.")
        else:
            print("[i] No ADMIN_USERNAME/ADMIN_PASSWORD found in environment. Skipping admin creation.")

        print("==================================================")
        print("[OK] Database setup completed successfully!")
        print("==================================================")


if __name__ == '__main__':
    init_database()
