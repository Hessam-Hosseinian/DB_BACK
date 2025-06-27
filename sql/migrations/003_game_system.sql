-- Game System Tables
-- ================================

CREATE TABLE IF NOT EXISTS game_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    config_template JSONB NOT NULL DEFAULT '{}'::JSONB,
    min_players SMALLINT NOT NULL DEFAULT 2,
    max_players SMALLINT NOT NULL DEFAULT 2,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS games (
    id BIGSERIAL PRIMARY KEY,
    game_type_id INTEGER NOT NULL REFERENCES game_types(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'active', 'completed', 'cancelled')),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    game_config JSONB NOT NULL DEFAULT '{}'::JSONB,
    winner_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS game_participants (
    game_id BIGINT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id),
    join_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    score INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'disconnected', 'finished')),
    stats JSONB DEFAULT '{}'::JSONB,
    PRIMARY KEY (game_id, user_id)
);

CREATE TABLE IF NOT EXISTS game_rounds (
    id BIGSERIAL PRIMARY KEY,
    game_id BIGINT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    round_number SMALLINT NOT NULL,
    question_id BIGINT NOT NULL REFERENCES questions(id),
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'completed')),
    time_limit_seconds INTEGER,
    points_possible INTEGER NOT NULL DEFAULT 100,
    UNIQUE (game_id, round_number)
);

CREATE TABLE IF NOT EXISTS round_answers (
    id BIGSERIAL PRIMARY KEY,
    round_id BIGINT NOT NULL REFERENCES game_rounds(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id),
    choice_id BIGINT NOT NULL REFERENCES question_choices(id),
    answer_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    is_correct BOOLEAN NOT NULL,
    points_earned INTEGER NOT NULL DEFAULT 0,
    UNIQUE (round_id, user_id)
);

-- Indexes
CREATE INDEX idx_games_status ON games(status) WHERE status = 'active';
CREATE INDEX idx_games_type_status ON games(game_type_id, status);
CREATE INDEX idx_game_participants_user ON game_participants(user_id, status);
CREATE INDEX idx_game_rounds_game ON game_rounds(game_id, round_number);
CREATE INDEX idx_round_answers_user ON round_answers(user_id, is_correct); 