import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    POSTGRES_USER = os.getenv('DB_USER')
    POSTGRES_PASSWORD = os.getenv('DB_PASSWORD')
    POSTGRES_HOST = os.getenv('DB_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('DB_PORT', '5432')
    POSTGRES_DB = os.getenv('DB_NAME')

    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
    }

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(',')

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    POSTGRES_USER = os.getenv('TEST_DB_USER', os.getenv('DB_USER'))
    POSTGRES_PASSWORD = os.getenv('TEST_DB_PASSWORD', os.getenv('DB_PASSWORD'))
    POSTGRES_HOST = os.getenv('TEST_DB_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('TEST_DB_PORT', '5432')
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
