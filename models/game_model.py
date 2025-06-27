from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from db.connection import get_connection
from db.query_loader import load_queries
from models.user_model import User
from utils.exceptions import GameError, ValidationError

QUERIES = load_queries("sql/queries/game_queries.sql")

class Game:
    def __init__(self, game_type_id: int, game_config: Dict = None, 
                 id: Optional[int] = None, status: str = 'pending',
                 winner_id: Optional[int] = None):
        self.id = id
        self.game_type_id = game_type_id
        self.status = status
        self.game_config = game_config or {}
        self.winner_id = winner_id
        self.participants: List[Dict[str, Any]] = []
        self.current_round: Optional[Dict[str, Any]] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None

    def validate(self) -> None:
        """Validate game data before saving"""
        if not self.game_type_id:
            raise ValidationError("Game type is required")
        if self.status not in ['pending', 'active', 'completed', 'cancelled']:
            raise ValidationError("Invalid game status")

    @staticmethod
    def get_available_game_types() -> List[Dict[str, Any]]:
        """Get list of available game types"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, config FROM game_types WHERE is_active = true")
            return [{'id': row[0], 'name': row[1], 'config': row[2]} for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def create(self, participant_ids: List[int]) -> None:
        """Create a new game with participants"""
        self.validate()
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["create_new_game"], 
                       (self.game_type_id, self.game_config, participant_ids))
            self.id = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to create game: {str(e)}")
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_id(cls, game_id: int) -> Optional['Game']:
        """Find game by ID with full details"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_active_game_details"], (game_id,))
            row = cur.fetchone()
            if not row:
                return None

            game = cls(
                id=row[0],
                game_type_id=row[1],
                status=row[2],
                game_config=row[3],
                winner_id=row[4]
            )
            game.start_time = row[5]
            game.end_time = row[6]
            game.last_activity = row[7]
            game.participants = row[8]
            
            # Get current round if game is active
            if game.status == 'active':
                cur.execute(QUERIES["get_current_game_round"], (game_id,))
                round_data = cur.fetchone()
                if round_data:
                    game.current_round = {
                        'id': round_data[0],
                        'question_text': round_data[1],
                        'difficulty': round_data[2],
                        'choices': round_data[3]
                    }
            
            return game
        finally:
            cur.close()
            conn.close()

    def submit_answer(self, user_id: int, round_id: int, choice_id: int, response_time_ms: int) -> Dict[str, Any]:
        """Submit an answer for the current round"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["submit_answer"], 
                       (round_id, user_id, choice_id, response_time_ms))
            result = cur.fetchone()
            conn.commit()
            
            return {
                'is_correct': result[0],
                'points_earned': result[1],
                'feedback': result[2]
            }
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to submit answer: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current game leaderboard"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_game_leaderboard"], (self.id,))
            return [
                {
                    'username': row[0],
                    'score': row[1],
                    'questions_answered': row[2],
                    'correct_answers': row[3],
                    'avg_response_time': row[4]
                }
                for row in cur.fetchall()
            ]
        finally:
            cur.close()
            conn.close()

    def finish_game(self, winner_id: Optional[int] = None) -> None:
        """End the game and update player stats"""
        if self.status != 'active':
            raise GameError("Only active games can be finished")
            
        conn = get_connection()
        try:
            cur = conn.cursor()
            self.winner_id = winner_id
            cur.execute("""
                UPDATE games 
                SET status = 'completed',
                    end_time = NOW(),
                    winner_id = %s
                WHERE id = %s
            """, (winner_id, self.id))
            
            self.status = 'completed'
            self.end_time = datetime.now()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to finish game: {str(e)}")
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def cleanup_inactive_games(timeout_minutes: int = 30) -> int:
        """Clean up inactive games"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE games 
                SET status = 'cancelled', 
                    end_time = NOW()
                WHERE status = 'active'
                AND last_activity < NOW() - interval '%s minutes'
                RETURNING id
            """, (timeout_minutes,))
            cleaned = cur.rowcount
            conn.commit()
            return cleaned
        finally:
            cur.close()
            conn.close()
