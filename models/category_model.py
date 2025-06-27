from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/queries/category_queries.sql")

class Category:
    def __init__(self, name, id=None, question_count=0):
        self.id = id
        self.name = name
        self.question_count = question_count

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["insert_a_new_category_and_return_its_id"], (self.name,))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return self

    def update(self, new_name):
        if not self.id:
            raise ValueError("Cannot update a category that hasn't been saved")
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["update_category_name"], (self.id, new_name))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if result:
            self.name = new_name
            return True
        return False

    def delete(self):
        if not self.id:
            raise ValueError("Cannot delete a category that hasn't been saved")
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["delete_category"], (self.id,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return result is not None

    @classmethod
    def find_by_name(cls, name):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_a_specific_category_by_name"], (name,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], name=row[1])
        return None

    @classmethod
    def find_by_id(cls, id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_category_by_id_with_question_count"], (id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], name=row[1], question_count=row[2])
        return None

    @classmethod
    def all(cls):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_all_categories_with_their_question_counts"])
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [cls(id=row[0], name=row[1], question_count=row[2]) for row in rows]
