from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/category.sql")

class Category:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["insert_category"], (self.name,))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def find_by_name(cls, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_category_by_name"], (name,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], name=row[1])
        return None

    @classmethod
    def all(cls):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_all_categories"])
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [cls(id=row[0], name=row[1]) for row in rows]
