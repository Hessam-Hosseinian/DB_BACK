from db.connection import get_connection
from db.query_loader import load_queries
from datetime import datetime
from psycopg2.errors import UniqueViolation

QUERIES = load_queries("sql/user.sql")

class User:
    def __init__(self, username, email, password, id=None, registered_at=None, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password = password 
        self.registered_at = registered_at
        self.is_admin = is_admin

    def to_dict(self, exclude_sensitive=True):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "is_admin": self.is_admin
        }
        if not exclude_sensitive:
            data["password"] = self.password
        return data

    def save(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["insert_user"], (
                self.username,
                self.email,
                self.password,
                datetime.utcnow(),
                self.is_admin
            ))
            self.id = cur.fetchone()[0]
            conn.commit()
        except UniqueViolation as e:
            raise ValueError("Username or email already exists")
        except Exception as e:
            raise Exception(f"Failed to save user: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def update(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["update_user"], (
                self.email,
                self.password,
                self.is_admin,
                self.id
            ))
            conn.commit()
        except UniqueViolation as e:
            raise ValueError("Email already exists")
        except Exception as e:
            raise Exception(f"Failed to update user: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def delete(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["delete_user"], (self.id,))
            conn.commit()
        except Exception as e:
            raise Exception(f"Failed to delete user: {str(e)}")
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_id(cls, user_id):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["get_user_by_id"], (user_id,))
            row = cur.fetchone()
            if row:
                return cls(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    registered_at=row[4],
                    is_admin=row[5]
                )
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_username(cls, username):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["get_user_by_username"], (username,))
            row = cur.fetchone()
            if row:
                return cls(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    registered_at=row[4],
                    is_admin=row[5]
                )
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_email(cls, email):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["get_user_by_email"], (email,))
            row = cur.fetchone()
            if row:
                return cls(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    registered_at=row[4],
                    is_admin=row[5]
                )
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def get_random_opponent(cls, exclude_id):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["get_random_opponent"], (exclude_id,))
            row = cur.fetchone()
            if row:
                return cls(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password=row[3],
                    registered_at=row[4],
                    is_admin=row[5]
                )
            return None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def get_leaderboard(cls, limit=10):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(QUERIES["get_leaderboard"], (limit,))
            rows = cur.fetchall()
            return [
                {
                    "user_id": row[0],
                    "username": row[1],
                    "wins": row[2],
                    "games_played": row[3],
                    "win_rate": round(row[2] / row[3] * 100, 2) if row[3] > 0 else 0
                }
                for row in rows
            ]
        finally:
            cur.close()
            conn.close()
