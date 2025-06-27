from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, text
from sqlalchemy.orm import relationship
from db.database import Base

class Leaderboard(Base):
    __tablename__ = 'leaderboard'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    games_played = Column(Integer, nullable=False, default=0)
    win_streak = Column(Integer, nullable=False, default=0)
    highest_score = Column(Integer, nullable=False, default=0)
    average_score = Column(Numeric(10, 2), nullable=False, default=0.0)
    last_played = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationship
    user = relationship('User', back_populates='leaderboard')

    @classmethod
    def get_global_leaderboard(cls, db, limit=10):
        """Get global leaderboard with detailed stats"""
        return db.execute(text("""
            SELECT u.username,
                   us.total_points,
                   us.games_played,
                   us.games_won,
                   ROUND(us.games_won::numeric / NULLIF(us.games_played, 0) * 100, 2) as win_rate,
                   ROUND(us.correct_answers::numeric / NULLIF(us.total_answers, 0) * 100, 2) as accuracy,
                   RANK() OVER (ORDER BY us.total_points DESC) as rank
            FROM user_stats us
            JOIN users u ON us.user_id = u.id
            WHERE us.games_played > 0
            LIMIT :limit
        """), {"limit": limit}).all()

    @classmethod
    def get_category_leaderboard(cls, db, category_id, limit=10):
        """Get category-specific leaderboard"""
        return db.execute(text("""
            SELECT u.username,
                   ucs.total_points,
                   ucs.games_played,
                   ucs.correct_answers,
                   ROUND(ucs.correct_answers::numeric / NULLIF(ucs.total_answers, 0) * 100, 2) as accuracy,
                   RANK() OVER (ORDER BY ucs.total_points DESC) as rank
            FROM user_category_stats ucs
            JOIN users u ON ucs.user_id = u.id
            WHERE ucs.category_id = :category_id AND ucs.games_played > 0
            LIMIT :limit
        """), {
            "category_id": category_id,
            "limit": limit
        }).all()

    @classmethod
    def get_daily_leaderboard(cls, db, category_id=None, limit=10):
        """Get daily leaderboard, optionally filtered by category"""
        return db.execute(text("""
            SELECT u.username,
                   l.score,
                   l.rank
            FROM leaderboards l
            JOIN users u ON l.user_id = u.id
            WHERE l.scope = 'daily'
              AND DATE(l.generated_at) = CURRENT_DATE
              AND (l.category_id = :category_id OR :category_id IS NULL)
            ORDER BY l.rank
            LIMIT :limit
        """), {
            "category_id": category_id,
            "limit": limit
        }).all()

    @classmethod
    def get_user_ranking_history(cls, db, user_id, limit=10):
        """Get user's ranking history across different scopes and categories"""
        return db.execute(text("""
            SELECT u.username,
                   l.scope,
                   l.score,
                   l.rank,
                   c.name as category_name,
                   l.generated_at
            FROM leaderboards l
            JOIN users u ON l.user_id = u.id
            LEFT JOIN categories c ON l.category_id = c.id
            WHERE l.user_id = :user_id
            ORDER BY l.generated_at DESC
            LIMIT :limit
        """), {
            "user_id": user_id,
            "limit": limit
        }).all()

    @classmethod
    def get_category_stats(cls, db):
        """Get statistics for all categories"""
        return db.execute(text("""
            SELECT c.name as category_name,
                   COUNT(DISTINCT q.id) as total_questions,
                   COUNT(DISTINCT gr.id) as times_played,
                   ROUND(AVG(q.success_rate), 2) as avg_success_rate,
                   COUNT(DISTINCT gp.user_id) as unique_players
            FROM categories c
            LEFT JOIN questions q ON c.id = q.category_id
            LEFT JOIN game_rounds gr ON q.id = gr.question_id
            LEFT JOIN round_answers ra ON gr.id = ra.round_id
            LEFT JOIN game_participants gp ON ra.user_id = gp.user_id
            GROUP BY c.id, c.name
        """)).all()

    @classmethod
    def refresh_daily_leaderboard(cls, db):
        """Refresh the daily leaderboard data"""
        db.execute(text("""
            WITH daily_scores AS (
                SELECT gp.user_id,
                       COALESCE(g.category_id, 0) as category_id,
                       SUM(gp.score) as daily_score,
                       RANK() OVER (PARTITION BY COALESCE(g.category_id, 0) 
                                   ORDER BY SUM(gp.score) DESC) as daily_rank
                FROM game_participants gp
                JOIN games g ON gp.game_id = g.id
                WHERE DATE(g.end_time) = CURRENT_DATE
                GROUP BY gp.user_id, COALESCE(g.category_id, 0)
            )
            INSERT INTO leaderboards (user_id, scope, category_id, rank, score)
            SELECT user_id, 'daily', 
                   NULLIF(category_id, 0),
                   daily_rank,
                   daily_score
            FROM daily_scores
            ON CONFLICT (user_id, scope, COALESCE(category_id, -1))
            DO UPDATE SET rank = EXCLUDED.rank,
                         score = EXCLUDED.score,
                         generated_at = NOW()
        """))
        db.commit()

    @classmethod
    def get_top_players(cls, db, limit=10):
        """Get top players ordered by score"""
        return db.query(cls).order_by(cls.score.desc()).limit(limit).all()

    @classmethod
    def get_player_rank(cls, db, user_id):
        """Get player's rank and percentile"""
        return db.execute("""
            SELECT rank, percentile, position 
            FROM leaderboard_rankings 
            WHERE user_id = :user_id
        """, {"user_id": user_id}).first()

    @classmethod
    def get_nearby_players(cls, db, user_id, range=2):
        """Get players ranked near the specified user"""
        rank_result = cls.get_player_rank(db, user_id)
        if not rank_result:
            return []
            
        position = rank_result.position
        return db.execute("""
            SELECT * FROM leaderboard_rankings
            WHERE position BETWEEN :min_pos AND :max_pos
            ORDER BY position
        """, {
            "min_pos": max(1, position - range),
            "max_pos": position + range
        }).all()

    def update_score(self, db, new_score):
        """Update player's score and related statistics"""
        db.execute("""
            SELECT update_user_score(:user_id, :new_score)
        """, {
            "user_id": self.user_id,
            "new_score": new_score
        })
        db.commit() 