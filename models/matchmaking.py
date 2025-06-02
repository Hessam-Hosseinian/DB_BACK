from db.connection import get_connection

class Matchmaker:
    def __init__(self):
        pass

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

    def find_match(self, user_id):
        """Find a match for the given user"""
        # First, add the user to the waiting pool
        self.add(user_id)
        
        # Try to find an opponent
        opponent_id = self.find_waiting_player(user_id)
        
        if opponent_id:
            # Remove both players from the waiting pool
            self.remove(user_id)
            self.remove(opponent_id)
        
        return opponent_id

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
