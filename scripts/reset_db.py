import os
import sys

# Ensure project root is on sys.path so imports work properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash


def reset_db():
    """
    Drop all tables, recreate schema, and optionally create an initial admin account
    using environment variables ADMIN_USERNAME and ADMIN_PASSWORD.
    """
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Re-create tables from the models
        db.create_all()
        print("[OK] Database tables dropped and re-created successfully.")

        # Read admin credentials from environment variables
        admin_user = os.environ.get('ADMIN_USERNAME')
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_pass = os.environ.get('ADMIN_PASSWORD')

        if admin_user and admin_pass:
            admin = User(
                username=admin_user,
                email=admin_email or f"{admin_user}@bloodbridge.in",
                password_hash=generate_password_hash(admin_pass),
                role='admin',
                is_admin=True,
            )
            db.session.add(admin)
            db.session.commit()
            print(f"[OK] Admin user '{admin_user}' created successfully from environment variables.")
        else:
            print("[i] No ADMIN_USERNAME/ADMIN_PASSWORD provided in .env. Skipping admin creation.")


if __name__ == '__main__':
    reset_db()
