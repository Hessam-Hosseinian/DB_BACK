from db.connection import get_connection
from models.question_model import Question
from datetime import datetime
from typing import Optional, Dict, Any

class Round:
    def __init__(self, game_id: int, round_number: int, question_id: int,
                 id: Optional[int] = None, status: str = 'pending',
                 time_limit_seconds: Optional[int] = None,
                 points_possible: int = 100):
        self.id = id
        self.game_id = game_id
        self.round_number = round_number
        self.question_id = question_id
        self.status = status
        self.time_limit_seconds = time_limit_seconds
        self.points_possible = points_possible
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO game_rounds (game_id, round_number, question_id, status, 
                                   time_limit_seconds, points_possible)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (self.game_id, self.round_number, self.question_id, self.status,
              self.time_limit_seconds, self.points_possible))
        self.id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

    def start_round(self):
        """Start the round"""
        if self.status != 'pending':
            raise ValueError("Round can only be started from pending status")
        
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE game_rounds 
                SET status = 'active',
                    start_time = NOW()
                WHERE id = %s
                RETURNING start_time
            """, (self.id,))
            self.start_time = cur.fetchone()[0]
            self.status = 'active'
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def end_round(self):
        """End the round"""
        if self.status != 'active':
            raise ValueError("Only active rounds can be ended")
        
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE game_rounds 
                SET status = 'completed',
                    end_time = NOW()
                WHERE id = %s
                RETURNING end_time
            """, (self.id,))
            self.end_time = cur.fetchone()[0]
            self.status = 'completed'
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def save_answer(self, user_id: int, choice_id: int, response_time_ms: int) -> Dict[str, Any]:
        """Submit an answer for this round"""
        conn = get_connection()
        cur = conn.cursor()
        try:
            # Check if answer already exists
            cur.execute("""
                SELECT 1 FROM round_answers
                WHERE round_id = %s AND user_id = %s
            """, (self.id, user_id))
            if cur.fetchone():
                raise ValueError("User has already answered this round")

            # Get correct choice and calculate points
            cur.execute("""
                SELECT is_correct 
                FROM question_choices 
                WHERE id = %s AND question_id = %s
            """, (choice_id, self.question_id))
            choice_row = cur.fetchone()
            if not choice_row:
                raise ValueError("Invalid choice")

            is_correct = choice_row[0]
            points_earned = self.calculate_points(response_time_ms) if is_correct else 0

            # Save answer
            cur.execute("""
                INSERT INTO round_answers 
                (round_id, user_id, choice_id, answer_time, response_time_ms, 
                 is_correct, points_earned)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s)
                RETURNING id
            """, (self.id, user_id, choice_id, response_time_ms, is_correct, points_earned))
            
            conn.commit()
            return {
                'is_correct': is_correct,
                'points_earned': points_earned
            }
        finally:
            cur.close()
            conn.close()

    def calculate_points(self, response_time_ms: int) -> int:
        """Calculate points based on response time"""
        if not self.time_limit_seconds:
            return self.points_possible
            
        max_time_ms = self.time_limit_seconds * 1000
        if response_time_ms >= max_time_ms:
            return 0
            
        # Points decrease linearly with time
        time_factor = 1 - (response_time_ms / max_time_ms)
        return int(self.points_possible * time_factor)

    @staticmethod
    def get_by_id(round_id: int) -> Optional['Round']:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT game_id, round_number, question_id, status,
                       time_limit_seconds, points_possible, start_time, end_time
                FROM game_rounds WHERE id = %s
            """, (round_id,))
            row = cur.fetchone()
            if not row:
                return None
                
            round = Round(
                game_id=row[0],
                round_number=row[1],
                question_id=row[2],
                status=row[3],
                time_limit_seconds=row[4],
                points_possible=row[5]
            )
            round.id = round_id
            round.start_time = row[6]
            round.end_time = row[7]
            return round
        finally:
            cur.close()
            conn.close()

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
