import pytest
import json
from app import create_app
from models.user_model import User
from models.user_stats_model import UserStats
from tests.test_config import TestConfig
from db.connection import get_connection

@pytest.fixture
def app():
    app = create_app('testing')
    app.config.from_object(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database():
    # Setup - create tables and insert test data
    conn = get_connection()
    cur = conn.cursor()
    
    # Drop existing tables if they exist
    cur.execute("""
        DROP TABLE IF EXISTS user_stats;
        DROP TABLE IF EXISTS users CASCADE;
    """)
    
    # Create tables with direct SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password TEXT NOT NULL,
            registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE,
            last_login TIMESTAMP WITH TIME ZONE,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
            CONSTRAINT username_length CHECK (length(username) >= 3),
            CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
        );

        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            games_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0
        );
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    yield  # this is where the testing happens
    
    # Teardown - drop tables
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS user_stats;
        DROP TABLE IF EXISTS users CASCADE;
    """)
    conn.commit()
    cur.close()
    conn.close()

def test_register_success(client, init_database):
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user_id' in data
    assert data['username'] == 'testuser'

def test_register_invalid_input(client, init_database):
    # Test short username
    response = client.post('/register', json={
        'username': 'te',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    assert response.status_code == 400
    
    # Test invalid email
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'TestPass123'
    })
    assert response.status_code == 400
    
    # Test weak password
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'weak'
    })
    assert response.status_code == 400

def test_login_success(client, init_database):
    # First register a user
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    
    # Then try to login
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user_id' in data
    assert data['username'] == 'testuser'

def test_login_invalid_credentials(client, init_database):
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'WrongPass123'
    })
    assert response.status_code == 401

def test_profile_authenticated(client, init_database):
    # Register and login
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    
    # Get profile
    response = client.get('/profile')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'testuser'
    assert data['email'] == 'test@example.com'

def test_profile_unauthenticated(client, init_database):
    response = client.get('/profile')
    assert response.status_code == 401

def test_update_profile(client, init_database):
    # Register and login
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    
    # Update profile
    response = client.put('/profile', json={
        'email': 'newemail@example.com',
        'password': 'NewPass123'
    })
    assert response.status_code == 200
    
    # Verify changes
    response = client.get('/profile')
    data = json.loads(response.data)
    assert data['email'] == 'newemail@example.com'

def test_logout(client, init_database):
    # Register and login
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    client.post('/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    
    # Logout
    response = client.post('/logout')
    assert response.status_code == 200
    
    # Verify we can't access profile after logout
    response = client.get('/profile')
    assert response.status_code == 401

def test_user_stats(client, init_database):
    # Register and login
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'TestPass123'
    })
    user_id = json.loads(response.data)['user_id']
    
    # Initialize stats (this would normally happen automatically)
    stats = UserStats(user_id=user_id)
    stats.save()
    
    # Get stats
    response = client.get('/me/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'games_played' in data
    assert 'wins' in data
    assert 'correct_answers' in data 