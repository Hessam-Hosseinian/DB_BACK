-- ================================
-- کاربران و پروفایل‌ها
-- ================================

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL CHECK (length(username) >= 3),
    email VARCHAR(120) UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    CONSTRAINT users_username_length CHECK (length(trim(username)) > 0)
) ;

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    bio TEXT,
    country VARCHAR(2),
    timezone VARCHAR(50),
    preferences JSONB DEFAULT '{}'::JSONB,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- New table for user sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- ================================
-- سوالات و دسته‌بندی
-- ================================

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    difficulty_level SMALLINT CHECK (difficulty_level BETWEEN 1 AND 5),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_parent CHECK (parent_id != id)
);

-- New table for category hierarchy materialized path
CREATE TABLE IF NOT EXISTS category_paths (
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    ancestor_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    depth INTEGER NOT NULL,
    PRIMARY KEY (category_id, ancestor_id)
);

CREATE TABLE IF NOT EXISTS questions (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT REFERENCES users(id),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    times_used INTEGER NOT NULL DEFAULT 0,
    success_rate DECIMAL(5,2) CHECK (success_rate BETWEEN 0 AND 100),
    last_used_at TIMESTAMP,
    CONSTRAINT question_text_length CHECK (length(trim(text)) > 0)
) ;



CREATE TABLE IF NOT EXISTS question_choices (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    choice_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    position CHAR(1) NOT NULL CHECK (position IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    UNIQUE (question_id, position),
    CONSTRAINT choice_text_length CHECK (length(trim(choice_text)) > 0)
);

-- New table for question tags
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS question_tags (
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)
);

CREATE TABLE IF NOT EXISTS question_reports (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id),
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'reviewed', 'dismissed')),
    reviewer_id BIGINT REFERENCES users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ================================
-- بازی‌ها، شرکت‌کنندگان، دورها
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
) ;



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

-- ================================
-- آمار، دستاورد، لیدربرد
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

-- New table for detailed category stats
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

-- ================================
-- دستاوردها
-- ================================

CREATE TABLE IF NOT EXISTS achievement_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES achievement_categories(id),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    criteria JSONB NOT NULL,
    points INTEGER NOT NULL DEFAULT 0,
    badge_url VARCHAR(255),
    difficulty VARCHAR(20) NOT NULL DEFAULT 'medium'
        CHECK (difficulty IN ('easy', 'medium', 'hard')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(id),
    earned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    game_id BIGINT REFERENCES games(id),
    PRIMARY KEY (user_id, achievement_id)
);

-- ================================
-- چت کاربران
-- ================================

CREATE TABLE IF NOT EXISTS chat_rooms (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(20) NOT NULL CHECK (type IN ('private', 'game', 'public')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    game_id BIGINT REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_room_members (
    room_id BIGINT NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (room_id, user_id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    room_id BIGINT NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reply_to_id BIGINT REFERENCES chat_messages(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ;


-- ================================
-- نوتیفیکیشن‌ها
-- ================================

CREATE TABLE IF NOT EXISTS notification_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    template TEXT NOT NULL,
    importance VARCHAR(20) NOT NULL DEFAULT 'normal'
        CHECK (importance IN ('low', 'normal', 'high'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    type_id INTEGER NOT NULL REFERENCES notification_types(id),
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data JSONB NOT NULL DEFAULT '{}'::JSONB,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    related_game_id BIGINT REFERENCES games(id)
) ;


-- ================================
-- ایندکس‌های مهم
-- ================================

-- User related indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role) WHERE role != 'user';
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expiry ON user_sessions(expires_at) WHERE is_active = TRUE;

-- Question related indexes
CREATE INDEX idx_questions_category ON questions(category_id, is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_questions_difficulty ON questions(difficulty) INCLUDE (category_id);
CREATE INDEX idx_question_choices_correct ON question_choices(question_id) WHERE is_correct = TRUE;
CREATE INDEX idx_question_tags_tag ON question_tags(tag_id);

-- Game related indexes
CREATE INDEX idx_games_status ON games(status) WHERE status = 'active';
CREATE INDEX idx_games_type_status ON games(game_type_id, status);
CREATE INDEX idx_game_participants_user ON game_participants(user_id, status);
CREATE INDEX idx_game_rounds_game ON game_rounds(game_id, round_number);
CREATE INDEX idx_round_answers_user ON round_answers(user_id, is_correct);

-- Achievement related indexes
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_date ON user_achievements(earned_at);

-- Chat related indexes
CREATE INDEX idx_chat_messages_room ON chat_messages(room_id, sent_at DESC);
CREATE INDEX idx_chat_messages_sender ON chat_messages(sender_id, sent_at DESC);

-- Notification related indexes
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(type_id, created_at DESC);

-- Stats related indexes
CREATE INDEX idx_user_stats_points ON user_stats(total_points DESC);
CREATE INDEX idx_leaderboards_scope_score ON leaderboards(scope, score DESC);
CREATE INDEX idx_user_category_stats_points ON user_category_stats(category_id, total_points DESC);

-- ================================
-- Materialized Views
-- ================================

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

CREATE UNIQUE INDEX idx_mv_top_players ON mv_top_players(id);

-- Refresh this view periodically with a cron job
