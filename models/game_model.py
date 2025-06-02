from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from db.connection import get_connection
from db.query_loader import load_queries
from models.user_model import User
from utils.exceptions import GameError, ValidationError

QUERIES = load_queries("sql/game.sql")

class Game:
    def __init__(self, player1_id: int, player2_id: int, status: str = 'pending', 
                 id: Optional[int] = None, winner_id: Optional[int] = None,
                 game_type: str = 'standard', game_config: Dict = None):
        self.id = id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.status = status
        self.winner_id = winner_id
        self.game_type = game_type
        self.game_config = game_config or {}
        self.player1_score = 0
        self.player2_score = 0
        self.total_rounds_played = 0
        self.score_history: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.player1_stats: Dict[str, Any] = {}
        self.player2_stats: Dict[str, Any] = {}
        self.achievements_earned: List[Dict[str, Any]] = []
        self.session_data: Dict[str, Any] = {}

    def validate(self) -> None:
        """Validate game data before saving"""
        if self.player1_id == self.player2_id:
            raise ValidationError("Players must be different")
        if self.status not in ['pending', 'active', 'finished']:
            raise ValidationError("Invalid game status")
        if self.game_type not in self.get_available_game_types():
            raise ValidationError("Invalid game type")

    @staticmethod
    def get_available_game_types() -> List[str]:
        """Get list of available game types"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT game_type FROM game_config")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    def save(self) -> None:
        """Save or update game in database with error handling"""
        self.validate()
        conn = get_connection()
        try:
            cur = conn.cursor()
            if self.id is None:
                # New game
                cur.execute(QUERIES["insert_game"], 
                          (self.player1_id, self.player2_id, self.status, 
                           self.game_type, self.game_config, 
                           self.player1_stats, self.player2_stats))
                self.id = cur.fetchone()[0]
            else:
                # Update existing game
                cur.execute("""
                    UPDATE games 
                    SET status = %s, winner_id = %s, player1_score = %s, 
                        player2_score = %s, end_time = %s, last_activity = CURRENT_TIMESTAMP,
                        player1_stats = %s, player2_stats = %s,
                        achievements_earned = %s, session_data = %s
                    WHERE id = %s
                """, (self.status, self.winner_id, self.player1_score, 
                      self.player2_score, self.end_time, self.player1_stats,
                      self.player2_stats, self.achievements_earned, 
                      self.session_data, self.id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to save game: {str(e)}")
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_id(cls, game_id: int) -> Optional['Game']:
        """Find game by ID with full details"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_game_stats"], (game_id,))
            row = cur.fetchone()
            if not row:
                return None

            game = cls(
                id=row[0],
                player1_id=row[1],
                player2_id=row[2],
                status=row[3],
                winner_id=row[4],
                game_type=row[5]
            )
            game.start_time = row[6]
            game.end_time = row[7]
            game.player1_score = row[8]
            game.player2_score = row[9]
            game.score_history = row[10]
            game.last_activity = row[11]
            game.total_rounds_played = row[12]
            game.player1_stats = row[13]
            game.player2_stats = row[14]
            game.achievements_earned = row[15]
            game.session_data = row[16]
            return game
        finally:
            cur.close()
            conn.close()

    def update_scores(self, round_results: Dict[str, Any]) -> None:
        """Update game scores with bonus points and achievements"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            
            # Calculate new scores including bonus points
            p1_points = round_results.get('player1_points', 0)
            p2_points = round_results.get('player2_points', 0)
            p1_bonus = round_results.get('player1_bonus', 0)
            p2_bonus = round_results.get('player2_bonus', 0)
            
            self.player1_score += (p1_points + p1_bonus)
            self.player2_score += (p2_points + p2_bonus)
            
            # Update score history with detailed information
            score_entry = {
                'round': round_results['round_number'],
                'player1': {'points': p1_points, 'bonus': p1_bonus},
                'player2': {'points': p2_points, 'bonus': p2_bonus},
                'timestamp': datetime.now().isoformat()
            }
            
            # Update player stats
            self.player1_stats = self._update_player_stats(self.player1_stats, 
                                                         p1_points, p1_bonus)
            self.player2_stats = self._update_player_stats(self.player2_stats, 
                                                         p2_points, p2_bonus)
            
            cur.execute(QUERIES["update_game_score"],
                       (self.player1_score, self.player2_score, 
                        [score_entry], self.player1_stats, 
                        self.player2_stats, self.id))
            conn.commit()
            
            # Check for achievements
            self._check_achievements(round_results)
            
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to update scores: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def _update_player_stats(self, stats: Dict, points: int, bonus: int) -> Dict:
        """Update player statistics"""
        stats['total_points'] = stats.get('total_points', 0) + points
        stats['total_bonus'] = stats.get('total_bonus', 0) + bonus
        stats['rounds_played'] = stats.get('rounds_played', 0) + 1
        return stats

    def _check_achievements(self, round_results: Dict[str, Any]) -> None:
        """Check and award achievements based on game progress"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            
            # Get available achievements
            cur.execute("SELECT * FROM achievements")
            achievements = cur.fetchall()
            
            for achievement in achievements:
                criteria = achievement[3]  # criteria is stored in JSONB
                
                if self._meets_criteria(criteria, round_results):
                    # Award achievement to relevant player(s)
                    for player_id in [self.player1_id, self.player2_id]:
                        cur.execute("""
                            INSERT INTO player_achievements 
                            (player_id, achievement_id, game_id)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (player_id, achievement_id) DO NOTHING
                        """, (player_id, achievement[0], self.id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise GameError(f"Failed to check achievements: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def _meets_criteria(self, criteria: Dict, round_results: Dict) -> bool:
        """Check if achievement criteria are met"""
        if criteria.get('min_score'):
            if (self.player1_score < criteria['min_score'] and 
                self.player2_score < criteria['min_score']):
                return False
                
        if criteria.get('consecutive_correct'):
            # Check for consecutive correct answers
            consecutive = criteria['consecutive_correct']
            p1_streak = self._get_streak(self.player1_id)
            p2_streak = self._get_streak(self.player2_id)
            return p1_streak >= consecutive or p2_streak >= consecutive
            
        if criteria.get('fast_answer'):
            # Check for fast answer achievements
            time_limit = criteria['fast_answer']
            answer_times = round_results.get('answer_times', {})
            return any(t and t <= time_limit for t in answer_times.values())
            
        return True

    def _get_streak(self, player_id: int) -> int:
        """Get player's current streak of correct answers"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) 
                FROM (
                    SELECT correct, 
                           row_number() OVER (ORDER BY timestamp DESC) as rn
                    FROM (
                        SELECT 
                            CASE 
                                WHEN player1_id = %s THEN player1_correct
                                ELSE player2_correct 
                            END as correct,
                            timestamp
                        FROM rounds r
                        JOIN games g ON r.game_id = g.id
                        WHERE g.id = %s
                        AND (
                            (player1_id = %s AND player1_correct IS NOT NULL) OR
                            (player2_id = %s AND player2_correct IS NOT NULL)
                        )
                        ORDER BY timestamp DESC
                    ) s
                    WHERE correct = true
                    AND rn = row_number() OVER (ORDER BY timestamp DESC)
                ) t
            """, (player_id, self.id, player_id, player_id))
            return cur.fetchone()[0]
        finally:
            cur.close()
            conn.close()

    def finish_game(self) -> Optional[int]:
        """Finish the game and determine winner with final calculations"""
        if self.status == 'finished':
            return self.winner_id

        self.status = 'finished'
        self.end_time = datetime.now()

        # Calculate final scores including all bonuses
        final_p1_score = self.player1_score
        final_p2_score = self.player2_score

        if final_p1_score > final_p2_score:
            self.winner_id = self.player1_id
        elif final_p2_score > final_p1_score:
            self.winner_id = self.player2_id
        # If scores are equal, winner_id remains None (draw)

        # Update session data with game summary
        self.session_data['game_summary'] = {
            'duration': (self.end_time - self.start_time).total_seconds(),
            'final_scores': {
                'player1': final_p1_score,
                'player2': final_p2_score
            },
            'achievements': self.achievements_earned
        }

        self.save()
        return self.winner_id

    @staticmethod
    def cleanup_inactive_games() -> int:
        """Clean up inactive games with detailed logging"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["cleanup_inactive_games"])
            affected = cur.rowcount
            conn.commit()
            return affected
        finally:
            cur.close()
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed game statistics"""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_game_stats"], (self.id,))
            row = cur.fetchone()
            
            stats = {
                'game_id': self.id,
                'status': self.status,
                'player1': {
                    'id': self.player1_id,
                    'score': self.player1_score,
                    'accuracy': row[13] if row else 0,
                    'stats': self.player1_stats
                },
                'player2': {
                    'id': self.player2_id,
                    'score': self.player2_score,
                    'accuracy': row[14] if row else 0,
                    'stats': self.player2_stats
                },
                'winner_id': self.winner_id,
                'total_rounds': self.total_rounds_played,
                'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
                'score_history': self.score_history,
                'timing_stats': row[16] if row else {},
                'achievements': self.achievements_earned
            }
            
            return stats
        finally:
            cur.close()
            conn.close()
