"""
BloodBridge Production Configuration Module
Provides environment-aware configuration classes for Development, Testing, and Production.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load variables from .env if present (root or backend)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
root_env = os.path.join(BASE_DIR, '.env')
if os.path.exists(root_env):
    load_dotenv(root_env)
else:
    load_dotenv()


class BaseConfig:
    """Base Configuration with enterprise security defaults."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-bloodbridge-key-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload limit
    
    # Emergency Hotline Config
    EMERGENCY_HOTLINE = os.environ.get('EMERGENCY_HOTLINE', '+91 7091379965')


class DevelopmentConfig(BaseConfig):
    """Development Environment Configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///schema.db'


class ProductionConfig(BaseConfig):
    """Production Environment Configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Enforce HTTPS only for cookies in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    """Testing Environment Configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary for easy lookup
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
