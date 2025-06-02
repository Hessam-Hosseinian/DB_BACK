--:create_user_stats
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_answers INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    total_bonus_points INTEGER DEFAULT 0,
    fastest_answer FLOAT DEFAULT NULL,
    average_answer_time FLOAT DEFAULT NULL,
    longest_win_streak INTEGER DEFAULT 0,
    current_win_streak INTEGER DEFAULT 0,
    perfect_games INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    rank_points INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_stats_rank ON user_stats(rank_points DESC);
CREATE INDEX IF NOT EXISTS idx_user_stats_wins ON user_stats(wins DESC);
CREATE INDEX IF NOT EXISTS idx_user_stats_xp ON user_stats(xp DESC);

--:init_user_stats
INSERT INTO user_stats (user_id) VALUES (%s);

--:increment_game
UPDATE user_stats 
SET games_played = games_played + 1,
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:increment_win
UPDATE user_stats 
SET wins = wins + 1,
    current_win_streak = current_win_streak + 1,
    longest_win_streak = GREATEST(longest_win_streak, current_win_streak + 1),
    rank_points = rank_points + 25,
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:increment_loss
UPDATE user_stats 
SET losses = losses + 1,
    current_win_streak = 0,
    rank_points = GREATEST(0, rank_points - 15),
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:increment_draw
UPDATE user_stats 
SET draws = draws + 1,
    rank_points = rank_points + 10,
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:update_answer_stats
UPDATE user_stats
SET total_answers = total_answers + 1,
    correct_answers = correct_answers + %s,
    total_points = total_points + %s,
    total_bonus_points = total_bonus_points + %s,
    fastest_answer = CASE 
        WHEN %s IS NOT NULL AND (fastest_answer IS NULL OR %s < fastest_answer)
        THEN %s
        ELSE fastest_answer
    END,
    average_answer_time = (average_answer_time * total_answers + %s) / (total_answers + 1),
    xp = xp + %s,
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:record_perfect_game
UPDATE user_stats
SET perfect_games = perfect_games + 1,
    rank_points = rank_points + 50,
    last_updated = CURRENT_TIMESTAMP
WHERE user_id = %s;

--:get_user_stats
SELECT 
    games_played, wins, losses, draws,
    correct_answers, total_answers,
    total_points, total_bonus_points,
    fastest_answer, average_answer_time,
    longest_win_streak, current_win_streak,
    perfect_games, xp, rank_points,
    last_updated
FROM user_stats 
WHERE user_id = %s;

--:get_leaderboard
SELECT 
    u.username,
    us.rank_points,
    us.wins,
    us.games_played,
    us.perfect_games,
    us.xp,
    ROUND(CAST(us.correct_answers AS FLOAT) / NULLIF(us.total_answers, 0) * 100, 2) as accuracy,
    us.fastest_answer,
    us.longest_win_streak
FROM user_stats us
JOIN users u ON u.id = us.user_id
ORDER BY us.rank_points DESC
LIMIT %s;

--:get_user_rank
WITH ranked_users AS (
    SELECT 
        user_id,
        RANK() OVER (ORDER BY rank_points DESC) as rank
    FROM user_stats
)
SELECT rank
FROM ranked_users
WHERE user_id = %s;
