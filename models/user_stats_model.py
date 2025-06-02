from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/user_stats.sql")

class UserStats:
    def __init__(self, user_id, games_played=0, wins=0, correct_answers=0, total_answers=0, xp=0):
        self.user_id = user_id
        self.games_played = games_played
        self.wins = wins
        self.correct_answers = correct_answers
        self.total_answers = total_answers
        self.xp = xp

    @classmethod
    def init_for_user(cls, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["init_user_stats"], (user_id,))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get(cls, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["get_user_stats"], (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(
                user_id=user_id,
                games_played=row[0],
                wins=row[1],
                correct_answers=row[2],
                total_answers=row[3],
                xp=row[4]
            )
        return None

    @classmethod
    def increment_game(cls, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["increment_game"], (user_id,))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def increment_win(cls, user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["increment_win"], (user_id,))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def increment_answer(cls, user_id, is_correct, xp_amount):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            QUERIES["increment_answer"],
            (1 if is_correct else 0, xp_amount, user_id)
        )
        conn.commit()
        cur.close()
        conn.close()
