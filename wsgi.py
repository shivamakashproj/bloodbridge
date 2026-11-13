"""
BloodBridge Production WSGI Entrypoint
Used by Gunicorn, uWSGI, Waitress, and cloud containers.
"""

from app import app

if __name__ == '__main__':
    app.run()
