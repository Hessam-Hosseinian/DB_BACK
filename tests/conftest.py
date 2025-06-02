import sys
import os
import pytest
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

from app import create_app
from models.user_model import User
from models.user_stats_model import UserStats
from config import config

def setup_test_db():
    """Set up a test database"""
    db_name = "test_db_" + os.urandom(8).hex()
    
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        dbname='postgres',
        user=config['testing'].POSTGRES_USER,
        password=config['testing'].POSTGRES_PASSWORD,
        host=config['testing'].POSTGRES_HOST
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur = conn.cursor()
    
    # Create test database
    cur.execute(f'CREATE DATABASE {db_name}')
    
    cur.close()
    conn.close()
    
    # Connect to the new test database
    conn = psycopg2.connect(
        dbname=db_name,
        user=config['testing'].POSTGRES_USER,
        password=config['testing'].POSTGRES_PASSWORD,
        host=config['testing'].POSTGRES_HOST
    )
    
    # Initialize schema
    with conn.cursor() as cur:
        # Drop all existing tables first
        cur.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        conn.commit()
        
        # Read and execute schema.sql
        schema_path = os.path.join(project_root, 'sql', 'schema.sql')
        with open(schema_path, 'r') as f:
            cur.execute(f.read())
    
    conn.commit()
    conn.close()
    
    return db_name

def teardown_test_db(db_name):
    """Clean up the test database"""
    conn = psycopg2.connect(
        dbname='postgres',
        user=config['testing'].POSTGRES_USER,
        password=config['testing'].POSTGRES_PASSWORD,
        host=config['testing'].POSTGRES_HOST
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cur = conn.cursor()
    
    # Terminate all connections to the test database
    cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
        AND pid <> pg_backend_pid()
    """)
    
    # Drop the test database
    cur.execute(f'DROP DATABASE IF EXISTS {db_name}')
    
    cur.close()
    conn.close()

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # Set up test database
    db_name = setup_test_db()
    
    # Create test app with the test database
    test_config = config['testing']
    test_config.POSTGRES_DB = db_name
    test_app = create_app(test_config)
    
    yield test_app
    
    # Clean up test database
    teardown_test_db(db_name)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Authentication headers for protected endpoints."""
    return {
        'Authorization': 'Bearer test-token'
    }

@pytest.fixture
def sample_game_data():
    """Sample game data for testing."""
    return {
        'category': 'Science',
        'type': 'multiple',
        'difficulty': 'medium',
        'question': 'What is the chemical symbol for gold?',
        'correct_answer': 'Au',
        'incorrect_answers': ['Ag', 'Fe', 'Cu']
    }

@pytest.fixture
def test_user():
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashed_password"
    )
    user.id = 1
    return user

@pytest.fixture
def test_user_stats():
    """Create test user stats."""
    stats = UserStats(
        user_id=1,
        games_played=5,
        wins=3,
        correct_answers=15,
        total_answers=20,
        xp=150
    )
    return stats 