-- Statistics and Leaderboard Tables
-- ================================

CREATE TABLE IF NOT EXISTS user_stats (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    games_played INTEGER NOT NULL DEFAULT 0,
    games_won INTEGER NOT NULL DEFAULT 0,
    total_points INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    total_answers INTEGER NOT NULL DEFAULT 0,
    average_response_time_ms INTEGER,
    highest_score INTEGER NOT NULL DEFAULT 0,
    current_streak INTEGER NOT NULL DEFAULT 0,
    best_streak INTEGER NOT NULL DEFAULT 0,
    last_played_at TIMESTAMP,
    stats_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_category_stats (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    games_played INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    total_answers INTEGER NOT NULL DEFAULT 0,
    total_points INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, category_id)
);

CREATE TABLE IF NOT EXISTS leaderboards (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scope VARCHAR(20) NOT NULL CHECK (scope IN ('daily', 'weekly', 'monthly', 'alltime')),
    category_id INTEGER REFERENCES categories(id),
    rank INTEGER NOT NULL,
    score INTEGER NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Materialized View for Top Players
CREATE MATERIALIZED VIEW mv_top_players AS
SELECT 
    u.id,
    u.username,
    us.total_points,
    us.games_won,
    us.games_played,
    ROUND(us.correct_answers::numeric / NULLIF(us.total_answers, 0) * 100, 2) as accuracy_rate
FROM users u
JOIN user_stats us ON u.id = us.user_id
WHERE us.games_played > 0
ORDER BY us.total_points DESC
WITH DATA;

-- Indexes
CREATE UNIQUE INDEX idx_mv_top_players ON mv_top_players(id);
CREATE INDEX idx_user_stats_points ON user_stats(total_points DESC);
CREATE INDEX idx_leaderboards_scope_score ON leaderboards(scope, score DESC);
CREATE INDEX idx_user_category_stats_points ON user_category_stats(category_id, total_points DESC); 