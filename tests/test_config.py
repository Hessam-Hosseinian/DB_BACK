import os
from config import Config

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test_secret_key'
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = False
    
    # Test database configuration
    DB_CONFIG = {
        "dbname": "postgres",  # Using default postgres database for tests
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": "5432"
    } 