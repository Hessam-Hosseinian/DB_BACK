from db.connection import get_connection

class Question:
    def __init__(self, id, text, choices, correct_answer, category):
        self.id = id
        self.text = text
        self.choices = choices
        self.correct_answer = correct_answer
        self.category = category

    @staticmethod
    def find_by_id(qid):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, text, choices, correct_answer, category
            FROM questions WHERE id = %s
        """, (qid,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return Question(id=row[0], text=row[1], choices=row[2], correct_answer=row[3], category=row[4])
        return None

    @staticmethod
    def get_3_random_by_category(category):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, text, choices, correct_answer, category
            FROM questions
            WHERE category = %s
            ORDER BY RANDOM()
            LIMIT 3
        """, (category,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [Question(id=r[0], text=r[1], choices=r[2], correct_answer=r[3], category=r[4]) for r in rows]

    @staticmethod
    def get_all_categories():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT category FROM questions")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
