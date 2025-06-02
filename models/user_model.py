from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/user.sql")

class User:
    def __init__(self, username, email, password, id=None, registered_at=None, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password = password 
        self.registered_at = registered_at
        self.is_admin = is_admin

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["insert_user"], (self.username, self.email, self.password))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def find_by_id(cls, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_user_by_id"], (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], username=row[1], email=row[2],
                       password=row[3], registered_at=row[4], is_admin=row[5])
        return None

    @classmethod
    def find_by_username(cls, username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_user_by_username"], (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], username=row[1], email=row[2],
                       password=row[3], registered_at=row[4], is_admin=row[5])
        return None

    @classmethod
    def get_random_opponent(cls, exclude_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, password, registered_at, is_admin "
            "FROM users WHERE id != %s ORDER BY RANDOM() LIMIT 1", (exclude_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return cls(id=row[0], username=row[1], email=row[2],
                       password=row[3], registered_at=row[4], is_admin=row[5])
        return None
