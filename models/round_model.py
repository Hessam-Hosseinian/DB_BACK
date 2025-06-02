from db.connection import get_connection
from models.question_model import Question

class Round:
    def __init__(self, game_id, round_number, chooser_id, id=None, category=None):
        self.id = id
        self.game_id = game_id
        self.round_number = round_number
        self.chooser_id = chooser_id
        self.category = category
        self.question_ids = []

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO rounds (game_id, round_number, chooser_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (self.game_id, self.round_number, self.chooser_id))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

    def set_category_and_questions(self, category, questions):
        self.category = category
        self.question_ids = [q.id for q in questions]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE rounds SET category = %s WHERE id = %s
        """, (category, self.id))

        for idx, q in enumerate(self.question_ids):
            cur.execute("""
                INSERT INTO round_questions (round_id, question_id, question_number)
                VALUES (%s, %s, %s)
            """, (self.id, q, idx + 1))

        conn.commit()
        cur.close()
        conn.close()

    def get_correct_answer(self, question_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT question_id FROM round_questions
            WHERE round_id = %s AND question_number = %s
        """, (self.id, question_number))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return None

        question = Question.find_by_id(row[0])
        return question.correct_answer

    def save_answer(self, user_id, question_number, answer, is_correct):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO round_answers (round_id, user_id, question_number, answer, is_correct)
            VALUES (%s, %s, %s, %s, %s)
        """, (self.id, user_id, question_number, answer, is_correct))
        conn.commit()
        cur.close()
        conn.close()

    def has_answered(self, user_id, question_number):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1 FROM round_answers
            WHERE round_id = %s AND user_id = %s AND question_number = %s
        """, (self.id, user_id, question_number))
        answered = cur.fetchone() is not None
        cur.close()
        conn.close()
        return answered

    @staticmethod
    def get_by_id(round_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT game_id, round_number, chooser_id, category
            FROM rounds WHERE id = %s
        """, (round_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return Round(game_id=row[0], round_number=row[1], chooser_id=row[2], category=row[3], id=round_id)
        return None

    def get_game(self):
        from models.game_model import Game
        return Game.find_by_id(self.game_id)

    @staticmethod
    def count_total_answers(game_id, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM round_answers
            WHERE user_id = %s AND round_id IN (
                SELECT id FROM rounds WHERE game_id = %s
            )
        """, (user_id, game_id))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result

    @staticmethod
    def total_correct_answers(game_id, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM round_answers
            WHERE user_id = %s AND is_correct = TRUE AND round_id IN (
                SELECT id FROM rounds WHERE game_id = %s
            )
        """, (user_id, game_id))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result
