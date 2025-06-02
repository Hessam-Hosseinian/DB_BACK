from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/game.sql")

class Game:
    def __init__(self, player1_id, player2_id, status='pending', id=None, winner_id=None):
        self.id = id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.status = status
        self.winner_id = winner_id

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(QUERIES["insert_game"], (self.player1_id, self.player2_id, self.status))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def find_by_id(cls, game_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, player1_id, player2_id, status, winner_id FROM games WHERE id = %s", (game_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return cls(id=row[0], player1_id=row[1], player2_id=row[2], status=row[3], winner_id=row[4])
        return None

    def finish_game_and_set_winner(self):
        conn = get_connection()
        cur = conn.cursor()

        # محاسبه تعداد پاسخ درست هر بازیکن از جدول rounds
        cur.execute("""
            SELECT
                SUM(CASE WHEN player1_correct THEN 1 ELSE 0 END),
                SUM(CASE WHEN player2_correct THEN 1 ELSE 0 END)
            FROM rounds
            WHERE game_id = %s
        """, (self.id,))
        scores = cur.fetchone()
        p1_score, p2_score = scores

        winner_id = None
        if p1_score > p2_score:
            winner_id = self.player1_id
        elif p2_score > p1_score:
            winner_id = self.player2_id
        # مساوی = None

        # به‌روزرسانی جدول games
        cur.execute("""
            UPDATE games
            SET status = 'finished',
                winner_id = %s,
                end_time = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (winner_id, self.id))

        conn.commit()
        cur.close()
        conn.close()

        return winner_id
