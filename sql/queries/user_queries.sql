-- User Authentication Queries
-- ================================

-- Get user by username with profile
SELECT u.*, up.*
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.username = $1 AND u.is_active = true;

-- Get user by email with profile
SELECT u.*, up.*
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.email = $1 AND u.is_active = true;

-- Get user by ID with profile
SELECT u.*, up.*
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.id = $1 AND u.is_active = true;

-- Create new user
INSERT INTO users (username, email, password_hash, role)
VALUES ($1, $2, $3, $4)
RETURNING id;

-- Create user profile
INSERT INTO user_profiles (user_id, display_name)
VALUES ($1, $2)
RETURNING *;

-- Create new user session
INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
VALUES ($1, $2, $3, $4, NOW() + INTERVAL '24 hours')
RETURNING id, session_token;

-- Get active session with user details
SELECT u.*, s.*
FROM user_sessions s
JOIN users u ON s.user_id = u.id
WHERE s.session_token = $1 AND s.is_active = true AND s.expires_at > NOW();

-- Update user profile
UPDATE user_profiles
SET display_name = COALESCE($2, display_name),
    avatar_url = COALESCE($3, avatar_url),
    bio = COALESCE($4, bio),
    country = COALESCE($5, country),
    timezone = COALESCE($6, timezone),
    preferences = preferences || $7::jsonb,
    updated_at = NOW()
WHERE user_id = $1
RETURNING *;

-- Update user
UPDATE users
SET email = COALESCE($1, email),
    password_hash = COALESCE($2, password_hash),
    last_login = COALESCE($3, last_login),
    is_active = COALESCE($4, is_active),
    role = COALESCE($5, role)
WHERE id = $6
RETURNING *;

-- Get user achievements with details
SELECT a.*, ac.name as category_name, ua.earned_at
FROM user_achievements ua
JOIN achievements a ON ua.achievement_id = a.id
JOIN achievement_categories ac ON a.category_id = ac.id
WHERE ua.user_id = $1
ORDER BY ua.earned_at DESC;

-- Get user stats with ranking
WITH user_rank AS (
    SELECT user_id, 
           RANK() OVER (ORDER BY total_points DESC) as global_rank
    FROM user_stats
)
SELECT us.*, ur.global_rank
FROM user_stats us
JOIN user_rank ur ON us.user_id = ur.user_id
WHERE us.user_id = $1;

-- Get random opponent
SELECT u.*, up.*
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.id != $1 
AND u.is_active = true 
AND EXISTS (
    SELECT 1 
    FROM user_stats us 
    WHERE us.user_id = u.id 
    AND us.games_played > 0
)
ORDER BY RANDOM()
LIMIT 1;

-- Deactivate user session
UPDATE user_sessions
SET is_active = false
WHERE session_token = $1
RETURNING id;

-- Initialize user stats
INSERT INTO user_stats (user_id)
VALUES ($1)
RETURNING *;

-- Get user progress
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
    WHERE us.user_id = $1
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
FROM user_data ud; 