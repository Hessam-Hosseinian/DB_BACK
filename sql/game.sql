--:create_games
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'active', 'finished'
    winner_id INTEGER,                      -- NULL until game ends
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    draw_points INTEGER DEFAULT 0,          -- For tie-breaker scenarios
    player1_score INTEGER DEFAULT 0,        -- Running score
    player2_score INTEGER DEFAULT 0,        -- Running score
    score_history JSONB DEFAULT '[]',       -- Track score progression
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Track game activity
    total_rounds_played INTEGER DEFAULT 0,  -- Track completed rounds
    game_type TEXT DEFAULT 'standard',      -- For future game variants
    game_config JSONB DEFAULT '{}',         -- Game-specific configuration
    player1_stats JSONB DEFAULT '{}',       -- Player 1 game-specific stats
    player2_stats JSONB DEFAULT '{}',       -- Player 2 game-specific stats
    achievements_earned JSONB DEFAULT '[]',  -- Achievements earned during game
    session_data JSONB DEFAULT '{}',        -- Session-specific data
    
    FOREIGN KEY (player1_id) REFERENCES users(id),
    FOREIGN KEY (player2_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id),
    
    CHECK (player1_id != player2_id),
    CHECK (status IN ('pending', 'active', 'finished'))
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_games_players ON games(player1_id, player2_id);
CREATE INDEX IF NOT EXISTS idx_games_status ON games(status);
CREATE INDEX IF NOT EXISTS idx_games_winner ON games(winner_id) WHERE winner_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_games_activity ON games(last_activity) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_games_type_status ON games(game_type, status);
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games(start_time);
CREATE INDEX IF NOT EXISTS idx_games_end_time ON games(end_time) WHERE end_time IS NOT NULL;

--:create_rounds
CREATE TABLE IF NOT EXISTS rounds (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    
    player1_answer CHAR(1),
    player2_answer CHAR(1),
    
    player1_correct BOOLEAN,
    player2_correct BOOLEAN,
    
    player1_answer_time TIMESTAMP,          -- Track answer timing
    player2_answer_time TIMESTAMP,          -- Track answer timing
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50),                   -- Store category
    round_status TEXT DEFAULT 'active',     -- 'active', 'completed'
    points_awarded INTEGER DEFAULT 1,       -- Configurable points per correct answer
    time_limit INTEGER DEFAULT 30,          -- Time limit in seconds for answering
    bonus_points INTEGER DEFAULT 0,         -- Extra points for quick answers
    round_stats JSONB DEFAULT '{}',         -- Round-specific statistics
    
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    
    CHECK (round_status IN ('active', 'completed')),
    CHECK (round_number BETWEEN 1 AND 5),
    CHECK (points_awarded > 0),
    CHECK (time_limit > 0)
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_rounds_game ON rounds(game_id);
CREATE INDEX IF NOT EXISTS idx_rounds_game_number ON rounds(game_id, round_number);
CREATE INDEX IF NOT EXISTS idx_rounds_status ON rounds(round_status);
CREATE INDEX IF NOT EXISTS idx_rounds_category ON rounds(category);
CREATE INDEX IF NOT EXISTS idx_rounds_timestamp ON rounds(timestamp);

--:create_achievements
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    criteria JSONB NOT NULL,                -- Achievement criteria
    points INTEGER DEFAULT 0,               -- Points awarded for achievement
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--:create_player_achievements
CREATE TABLE IF NOT EXISTS player_achievements (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    game_id INTEGER,                        -- Game where achievement was earned
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id),
    FOREIGN KEY (game_id) REFERENCES games(id),
    
    UNIQUE (player_id, achievement_id)      -- Each achievement once per player
);

--:create_game_config
CREATE TABLE IF NOT EXISTS game_config (
    id SERIAL PRIMARY KEY,
    game_type TEXT NOT NULL UNIQUE,
    config JSONB NOT NULL DEFAULT '{}',     -- Game type specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--:insert_game
INSERT INTO games (
    player1_id, player2_id, status, game_type, 
    game_config, player1_stats, player2_stats
)
VALUES (%s, %s, %s, %s, %s, %s, %s) 
RETURNING id;

--:insert_round
INSERT INTO rounds (
    game_id, round_number, question_id, 
    category, points_awarded, time_limit, round_stats
)
VALUES (%s, %s, %s, %s, %s, %s, %s) 
RETURNING id;

--:update_game_score
UPDATE games 
SET player1_score = %s,
    player2_score = %s,
    score_history = score_history || %s::jsonb,
    last_activity = CURRENT_TIMESTAMP,
    total_rounds_played = 
        (SELECT COUNT(DISTINCT round_number) 
         FROM rounds 
         WHERE game_id = games.id AND round_status = 'completed'),
    player1_stats = player1_stats || %s::jsonb,
    player2_stats = player2_stats || %s::jsonb
WHERE id = %s;

--:record_answer
UPDATE rounds
SET player1_answer = CASE WHEN %s = player1_id THEN %s ELSE player1_answer END,
    player2_answer = CASE WHEN %s = player2_id THEN %s ELSE player2_answer END,
    player1_answer_time = CASE WHEN %s = player1_id THEN CURRENT_TIMESTAMP ELSE player1_answer_time END,
    player2_answer_time = CASE WHEN %s = player2_id THEN CURRENT_TIMESTAMP ELSE player2_answer_time END,
    bonus_points = CASE 
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - timestamp)) <= 10 THEN 2
        WHEN EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - timestamp)) <= 20 THEN 1
        ELSE 0
    END,
    round_status = CASE 
        WHEN player1_answer IS NOT NULL AND player2_answer IS NOT NULL 
        THEN 'completed' 
        ELSE 'active' 
    END,
    round_stats = round_stats || 
        jsonb_build_object(
            'answer_times', jsonb_build_object(
                'player1', EXTRACT(EPOCH FROM (player1_answer_time - timestamp)),
                'player2', EXTRACT(EPOCH FROM (player2_answer_time - timestamp))
            )
        )
WHERE id = %s;

--:get_game_stats
SELECT 
    g.*,
    COUNT(DISTINCT r.round_number) as total_rounds,
    AVG(CASE WHEN r.player1_correct THEN 1 ELSE 0 END) as player1_accuracy,
    AVG(CASE WHEN r.player2_correct THEN 1 ELSE 0 END) as player2_accuracy,
    MAX(r.timestamp) as last_round_time,
    SUM(r.bonus_points) as total_bonus_points,
    jsonb_build_object(
        'fastest_answer', MIN(
            LEAST(
                EXTRACT(EPOCH FROM (r.player1_answer_time - r.timestamp)),
                EXTRACT(EPOCH FROM (r.player2_answer_time - r.timestamp))
            )
        ),
        'average_answer_time', AVG(
            (
                EXTRACT(EPOCH FROM (r.player1_answer_time - r.timestamp)) +
                EXTRACT(EPOCH FROM (r.player2_answer_time - r.timestamp))
            ) / 2
        )
    ) as timing_stats
FROM games g
LEFT JOIN rounds r ON g.id = r.game_id
WHERE g.id = %s
GROUP BY g.id;

--:cleanup_inactive_games
UPDATE games
SET status = 'finished',
    end_time = CURRENT_TIMESTAMP,
    session_data = session_data || 
        jsonb_build_object('cleanup_reason', 'inactivity')
WHERE status = 'active'
AND last_activity < NOW() - INTERVAL '30 minutes';

--:get_player_achievements
SELECT 
    a.name,
    a.description,
    a.points,
    pa.earned_at,
    pa.game_id
FROM player_achievements pa
JOIN achievements a ON pa.achievement_id = a.id
WHERE pa.player_id = %s
ORDER BY pa.earned_at DESC;

--:get_game_config
SELECT config
FROM game_config
WHERE game_type = %s;
