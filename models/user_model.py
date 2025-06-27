from db.connection import get_connection
from datetime import datetime, timedelta
from psycopg2.errors import UniqueViolation
from typing import Optional, Dict, Any, List

class User:
    def __init__(self, username: str, email: str, password_hash: str, id: Optional[int] = None,
                 created_at: Optional[datetime] = None, last_login: Optional[datetime] = None,
                 role: str = 'user', is_active: bool = True, profile: Optional[Dict[str, Any]] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.role = role
        self.is_active = is_active
        self.profile = profile or {}

    def to_dict(self, exclude_sensitive: bool = True) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "role": self.role,
            "is_active": self.is_active,
            "profile": self.profile
        }
        if not exclude_sensitive:
            data["password_hash"] = self.password_hash
        return data

    @staticmethod
    def _create_user_from_row(row: tuple) -> 'User':
        """Create a User instance from a database row"""
        user = User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            last_login=row[5],
            role=row[7],
            is_active=row[6],
            profile={
                "display_name": row[9],
                "avatar_url": row[10],
                "bio": row[11],
                "country": row[12],
                "timezone": row[13],
                "preferences": row[14] or {},
                "updated_at": row[15]
            } if row[9] is not None else None
        )
        return user

    def save(self) -> None:
        """Save new user to database"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Start transaction
            cur.execute("BEGIN")
            
            # Insert user
            cur.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (self.username, self.email, self.password_hash, self.role))
            self.id = cur.fetchone()[0]
            
            # Create profile
            cur.execute("""
                INSERT INTO user_profiles (user_id, display_name)
                VALUES (%s, %s)
            """, (self.id, self.username))
            
            # Initialize stats
            cur.execute("""
                INSERT INTO user_stats (user_id)
                VALUES (%s)
            """, (self.id,))
            
            cur.execute("COMMIT")
            
        except UniqueViolation:
            cur.execute("ROLLBACK")
            raise ValueError("Username or email already exists")
        except Exception as e:
            cur.execute("ROLLBACK")
            raise Exception(f"Failed to save user: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def update(self, data: Dict[str, Any]) -> None:
        """Update user data and profile"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Start transaction
            cur.execute("BEGIN")
            
            # Update user
            if any(key in data for key in ['email', 'password_hash', 'role', 'is_active']):
                cur.execute("""
                    UPDATE users
                    SET email = COALESCE(%s, email),
                        password_hash = COALESCE(%s, password_hash),
                        role = COALESCE(%s, role),
                        is_active = COALESCE(%s, is_active)
                    WHERE id = %s
                    RETURNING *
                """, (
                    data.get('email'),
                    data.get('password_hash'),
                    data.get('role'),
                    data.get('is_active'),
                    self.id
                ))
                user_data = cur.fetchone()
                if user_data:
                    self.email = user_data[2]
                    self.password_hash = user_data[3]
                    self.role = user_data[7]
                    self.is_active = user_data[6]
            
            # Update profile
            if any(key in data for key in ['display_name', 'avatar_url', 'bio', 'country', 'timezone', 'preferences']):
                cur.execute("""
                    UPDATE user_profiles
                    SET display_name = COALESCE(%s, display_name),
                        avatar_url = COALESCE(%s, avatar_url),
                        bio = COALESCE(%s, bio),
                        country = COALESCE(%s, country),
                        timezone = COALESCE(%s, timezone),
                        preferences = COALESCE(%s, preferences),
                        updated_at = NOW()
                    WHERE user_id = %s
                    RETURNING *
                """, (
                    data.get('display_name'),
                    data.get('avatar_url'),
                    data.get('bio'),
                    data.get('country'),
                    data.get('timezone'),
                    data.get('preferences'),
                    self.id
                ))
                profile_data = cur.fetchone()
                if profile_data:
                    self.profile = {
                        "display_name": profile_data[1],
                        "avatar_url": profile_data[2],
                        "bio": profile_data[3],
                        "country": profile_data[4],
                        "timezone": profile_data[5],
                        "preferences": profile_data[6]
                    }
            
            cur.execute("COMMIT")
            
        except UniqueViolation:
            cur.execute("ROLLBACK")
            raise ValueError("Email already exists")
        except Exception as e:
            cur.execute("ROLLBACK")
            raise Exception(f"Failed to update user: {str(e)}")
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """Find user by ID"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.*, up.*
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.id = %s AND u.is_active = true
            """, (user_id,))
            row = cur.fetchone()
            return cls._create_user_from_row(row) if row else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Find user by username"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.*, up.*
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.username = %s AND u.is_active = true
            """, (username,))
            row = cur.fetchone()
            return cls._create_user_from_row(row) if row else None
        finally:
            cur.close()
            conn.close()

    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Find user by email"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.*, up.*
                FROM users u
                LEFT JOIN user_profiles up ON u.id = up.user_id
                WHERE u.email = %s AND u.is_active = true
            """, (email,))
            row = cur.fetchone()
            return cls._create_user_from_row(row) if row else None
        finally:
            cur.close()
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                WITH user_data AS (
                    SELECT 
                        us.*,
                        COUNT(DISTINCT ua.achievement_id) as achievements_count,
                        COUNT(DISTINCT gp.game_id) as games_participated,
                        COUNT(DISTINCT CASE WHEN g.winner_id = us.user_id THEN g.id END) as games_won
                    FROM user_stats us
                    LEFT JOIN user_achievements ua ON us.user_id = ua.user_id
                    LEFT JOIN game_participants gp ON us.user_id = gp.user_id
                    LEFT JOIN games g ON gp.game_id = g.id
                    WHERE us.user_id = %s
                    GROUP BY us.user_id, us.total_points, us.games_played, us.games_won,
                             us.correct_answers, us.total_answers, us.average_response_time_ms,
                             us.highest_score, us.current_streak, us.best_streak, us.last_played_at,
                             us.stats_updated_at
                )
                SELECT 
                    ud.*,
                    RANK() OVER (ORDER BY ud.total_points DESC) as global_rank,
                    ROUND(ud.games_won::numeric / NULLIF(ud.games_played, 0) * 100, 2) as win_rate,
                    ROUND(ud.correct_answers::numeric / NULLIF(ud.total_answers, 0) * 100, 2) as accuracy
                FROM user_data ud
            """, (self.id,))
            row = cur.fetchone()
            if not row:
                return {}
            
            return {
                "total_points": row[2],
                "games_played": row[3],
                "games_won": row[4],
                "correct_answers": row[5],
                "total_answers": row[6],
                "average_response_time_ms": row[7],
                "highest_score": row[8],
                "current_streak": row[9],
                "best_streak": row[10],
                "last_played_at": row[11].isoformat() if row[11] else None,
                "achievements_count": row[13],
                "games_participated": row[14],
                "global_rank": row[16],
                "win_rate": row[17],
                "accuracy": row[18]
            }
        finally:
            cur.close()
            conn.close()

    def get_achievements(self) -> List[Dict[str, Any]]:
        """Get user achievements"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT a.*, ac.name as category_name, ua.earned_at
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                JOIN achievement_categories ac ON a.category_id = ac.id
                WHERE ua.user_id = %s
                ORDER BY ua.earned_at DESC
            """, (self.id,))
            return [{
                "id": row[0],
                "name": row[2],
                "description": row[3],
                "points": row[5],
                "badge_url": row[6],
                "difficulty": row[7],
                "category_name": row[9],
                "earned_at": row[10].isoformat()
            } for row in cur.fetchall()]
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def create_session(user_id: int, token: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Create a new user session"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Set expiration time (e.g., 24 hours from now)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            cur.execute("""
                INSERT INTO user_sessions 
                (user_id, session_token, ip_address, user_agent, expires_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, started_at, expires_at
            """, (user_id, token, ip_address, user_agent, expires_at))
            
            session_data = cur.fetchone()
            
            # Update last_login
            cur.execute("""
                UPDATE users 
                SET last_login = NOW() 
                WHERE id = %s
            """, (user_id,))
            
            conn.commit()
            
            return {
                "session_id": session_data[0],
                "started_at": session_data[1],
                "expires_at": session_data[2]
            }
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def end_session(token: str) -> bool:
        """End a user session"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE user_sessions 
                SET is_active = false 
                WHERE session_token = %s AND is_active = true
                RETURNING id
            """, (token,))
            
            session_ended = cur.fetchone() is not None
            conn.commit()
            return session_ended
        finally:
            cur.close()
            conn.close()
