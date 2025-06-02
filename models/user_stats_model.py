from datetime import datetime
from typing import Optional, Dict, Any, List
from db.connection import get_connection
from db.query_loader import load_queries

QUERIES = load_queries("sql/user_stats.sql")

class UserStats:
    def __init__(self, user_id: int, games_played: int = 0, wins: int = 0, 
                 losses: int = 0, draws: int = 0, correct_answers: int = 0, 
                 total_answers: int = 0, total_points: int = 0, 
                 total_bonus_points: int = 0, fastest_answer: Optional[float] = None,
                 average_answer_time: Optional[float] = None, 
                 longest_win_streak: int = 0, current_win_streak: int = 0,
                 perfect_games: int = 0, xp: int = 0, rank_points: int = 0,
                 last_updated: Optional[datetime] = None):
        self.user_id = user_id
        self.games_played = games_played
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.correct_answers = correct_answers
        self.total_answers = total_answers
        self.total_points = total_points
        self.total_bonus_points = total_bonus_points
        self.fastest_answer = fastest_answer
        self.average_answer_time = average_answer_time
        self.longest_win_streak = longest_win_streak
        self.current_win_streak = current_win_streak
        self.perfect_games = perfect_games
        self.xp = xp
        self.rank_points = rank_points
        self.last_updated = last_updated or datetime.now()

    def save(self):
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO user_stats (user_id, games_played, wins, correct_answers, total_answers, xp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET games_played = %s,
                    wins = %s,
                    correct_answers = %s,
                    total_answers = %s,
                    xp = %s
            """, (
                self.user_id, self.games_played, self.wins, self.correct_answers, self.total_answers, self.xp,
                self.games_played, self.wins, self.correct_answers, self.total_answers, self.xp
            ))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def to_dict(self) -> Dict[str, Any]:
        accuracy = round((self.correct_answers / self.total_answers) * 100, 2) if self.total_answers else 0
        win_rate = round((self.wins / self.games_played) * 100, 2) if self.games_played else 0
        return {
            "games_played": self.games_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "win_rate": win_rate,
            "perfect_games": self.perfect_games,
            "correct_answers": self.correct_answers,
            "total_answers": self.total_answers,
            "accuracy": accuracy,
            "fastest_answer": round(self.fastest_answer, 2) if self.fastest_answer else None,
            "average_answer_time": round(self.average_answer_time, 2) if self.average_answer_time else None,
            "total_points": self.total_points,
            "total_bonus_points": self.total_bonus_points,
            "rank_points": self.rank_points,
            "xp": self.xp,
            "current_win_streak": self.current_win_streak,
            "longest_win_streak": self.longest_win_streak,
            "last_updated": self.last_updated.isoformat()
        }

    @classmethod
    def get(cls, user_id: int) -> Optional['UserStats']:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_user_stats"], (user_id,))
            row = cur.fetchone()
            if not row:
                return None

            stats = cls(
                user_id=user_id,
                games_played=row[0],
                wins=row[1],
                losses=row[2],
                draws=row[3],
                correct_answers=row[4],
                total_answers=row[5],
                total_points=row[6],
                total_bonus_points=row[7],
                fastest_answer=row[8],
                average_answer_time=row[9],
                longest_win_streak=row[10],
                current_win_streak=row[11],
                perfect_games=row[12],
                xp=row[13],
                rank_points=row[14],
                last_updated=row[15]
            )
            return stats
        finally:
            cur.close()
            conn.close()

    def update_game_result(self, won: bool, drew: bool = False) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["increment_game"], (self.user_id,))
            if drew:
                cur.execute(QUERIES["increment_draw"], (self.user_id,))
            elif won:
                cur.execute(QUERIES["increment_win"], (self.user_id,))
            else:
                cur.execute(QUERIES["increment_loss"], (self.user_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def update_answer_stats(self, is_correct: bool, points: int, bonus_points: int, answer_time: float, xp_earned: int) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                QUERIES["update_answer_stats"],
                (1 if is_correct else 0, points, bonus_points,
                 answer_time, answer_time, answer_time, answer_time,
                 xp_earned, self.user_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def record_perfect_game(self) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["record_perfect_game"], (self.user_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_leaderboard"], (limit,))
            leaderboard = [
                {
                    "username": row[0],
                    "rank_points": row[1],
                    "wins": row[2],
                    "games_played": row[3],
                    "perfect_games": row[4],
                    "xp": row[5],
                    "accuracy": row[6],
                    "fastest_answer": round(row[7], 2) if row[7] else None,
                    "longest_streak": row[8]
                }
                for row in cur.fetchall()
            ]
            return leaderboard
        finally:
            cur.close()
            conn.close()

    def get_rank(self) -> int:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["get_user_rank"], (self.user_id,))
            rank = cur.fetchone()[0]
            return rank
        finally:
            cur.close()
            conn.close()

    @classmethod
    def init_for_user(cls, user_id: int) -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(QUERIES["init_user_stats"], (user_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()

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
