from db.connection import get_connection

class Matchmaking:
    @staticmethod
    def add(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO waiting_players (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def remove(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM waiting_players WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def find_waiting_player(exclude_user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id FROM waiting_players
            WHERE user_id != %s
            ORDER BY joined_at ASC
            LIMIT 1
        """, (exclude_user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
