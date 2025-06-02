-- Leaderboard table to store user scores and rankings
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    games_played INTEGER NOT NULL DEFAULT 0,
    win_streak INTEGER NOT NULL DEFAULT 0,
    highest_score INTEGER NOT NULL DEFAULT 0,
    average_score DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    last_played TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_leaderboard_score ON leaderboard(score DESC);
CREATE INDEX idx_leaderboard_user_id ON leaderboard(user_id);
CREATE INDEX idx_leaderboard_last_played ON leaderboard(last_played DESC);

-- Create materialized view for caching complex leaderboard calculations
CREATE MATERIALIZED VIEW leaderboard_rankings AS
WITH user_stats AS (
    SELECT 
        l.user_id,
        u.username,
        l.score,
        l.games_played,
        l.win_streak,
        l.highest_score,
        l.average_score,
        l.last_played,
        DENSE_RANK() OVER (ORDER BY l.score DESC) as rank,
        PERCENT_RANK() OVER (ORDER BY l.score DESC) as percentile,
        ROW_NUMBER() OVER (ORDER BY l.score DESC, l.last_played DESC) as position
    FROM leaderboard l
    JOIN users u ON l.user_id = u.id
)
SELECT * FROM user_stats;

-- Create index on materialized view
CREATE UNIQUE INDEX idx_leaderboard_rankings_user_id ON leaderboard_rankings(user_id);

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_leaderboard_rankings()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard_rankings;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger to refresh materialized view when leaderboard changes
CREATE TRIGGER refresh_leaderboard_rankings_trigger
AFTER INSERT OR UPDATE OR DELETE ON leaderboard
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_leaderboard_rankings();

-- Function to update user scores
CREATE OR REPLACE FUNCTION update_user_score(
    p_user_id INTEGER,
    p_new_score INTEGER
)
RETURNS void AS $$
DECLARE
    current_score INTEGER;
BEGIN
    SELECT score INTO current_score
    FROM leaderboard
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO leaderboard (user_id, score, games_played, highest_score)
        VALUES (p_user_id, p_new_score, 1, p_new_score);
    ELSE
        UPDATE leaderboard
        SET 
            score = score + p_new_score,
            games_played = games_played + 1,
            highest_score = GREATEST(highest_score, p_new_score),
            average_score = ((average_score * games_played) + p_new_score) / (games_played + 1),
            last_played = CURRENT_TIMESTAMP
        WHERE user_id = p_user_id;
    END IF;
END;
$$ LANGUAGE plpgsql; 