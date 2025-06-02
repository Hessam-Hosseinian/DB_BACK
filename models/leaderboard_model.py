from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric
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