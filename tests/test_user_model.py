import pytest
from models.user_model import User
from db.connection import get_connection
from datetime import datetime
from psycopg2.errors import UniqueViolation

@pytest.fixture
def init_database():
    # Setup - create tables
    conn = get_connection()
    cur = conn.cursor()
    
    # Drop existing tables if they exist
    cur.execute("""
        DROP TABLE IF EXISTS user_stats;
        DROP TABLE IF EXISTS users CASCADE;
    """)
    
    # Create tables with direct SQL (not using the query file)
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

def test_user_creation(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "hashedpassword123"
    assert user.id is None
    assert user.is_admin is False

def test_user_save(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    assert user.id is not None
    
    # Verify in database
    saved_user = User.find_by_id(user.id)
    assert saved_user is not None
    assert saved_user.username == "testuser"
    assert saved_user.email == "test@example.com"

def test_user_duplicate_username(init_database):
    user1 = User(
        username="testuser",
        email="test1@example.com",
        password="hashedpassword123"
    )
    user1.save()
    
    user2 = User(
        username="testuser",
        email="test2@example.com",
        password="hashedpassword123"
    )
    with pytest.raises(ValueError):
        user2.save()

def test_user_duplicate_email(init_database):
    user1 = User(
        username="testuser1",
        email="test@example.com",
        password="hashedpassword123"
    )
    user1.save()
    
    user2 = User(
        username="testuser2",
        email="test@example.com",
        password="hashedpassword123"
    )
    with pytest.raises(ValueError):
        user2.save()

def test_find_by_username(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    
    found_user = User.find_by_username("testuser")
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.email == user.email
    
    not_found_user = User.find_by_username("nonexistent")
    assert not_found_user is None

def test_find_by_email(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    
    found_user = User.find_by_email("test@example.com")
    assert found_user is not None
    assert found_user.id == user.id
    assert found_user.username == user.username
    
    not_found_user = User.find_by_email("nonexistent@example.com")
    assert not_found_user is None

def test_user_update(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    
    user.email = "newemail@example.com"
    user.password = "newhashedpassword123"
    user.update()
    
    updated_user = User.find_by_id(user.id)
    assert updated_user.email == "newemail@example.com"
    assert updated_user.password == "newhashedpassword123"

def test_user_delete(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    user_id = user.id
    
    user.delete()
    
    deleted_user = User.find_by_id(user_id)
    assert deleted_user is None

def test_get_random_opponent(init_database):
    user1 = User(
        username="testuser1",
        email="test1@example.com",
        password="hashedpassword123"
    )
    user1.save()
    
    user2 = User(
        username="testuser2",
        email="test2@example.com",
        password="hashedpassword123"
    )
    user2.save()
    
    opponent = User.get_random_opponent(user1.id)
    assert opponent is not None
    assert opponent.id == user2.id

def test_get_leaderboard(init_database):
    # Create some users with different stats
    user1 = User(username="user1", email="user1@example.com", password="pass1")
    user1.save()
    user2 = User(username="user2", email="user2@example.com", password="pass2")
    user2.save()
    
    # Add some game results (this would require the games table to be set up)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            player1_id INTEGER REFERENCES users(id),
            player2_id INTEGER REFERENCES users(id),
            winner_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert some game results
    cur.execute("""
        INSERT INTO games (player1_id, player2_id, winner_id)
        VALUES (%s, %s, %s)
    """, (user1.id, user2.id, user1.id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    leaderboard = User.get_leaderboard(limit=10)
    assert len(leaderboard) > 0
    assert leaderboard[0]['username'] in ['user1', 'user2']
    assert 'wins' in leaderboard[0]
    assert 'games_played' in leaderboard[0]
    assert 'win_rate' in leaderboard[0]

def test_to_dict(init_database):
    user = User(
        username="testuser",
        email="test@example.com",
        password="hashedpassword123"
    )
    user.save()
    
    user_dict = user.to_dict()
    assert 'id' in user_dict
    assert 'username' in user_dict
    assert 'email' in user_dict
    assert 'is_admin' in user_dict
    assert 'password' not in user_dict  # Should not include sensitive data
    
    user_dict_with_sensitive = user.to_dict(exclude_sensitive=False)
    assert 'password' in user_dict_with_sensitive 