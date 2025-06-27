-- Question System Tables
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
);

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

-- Indexes
CREATE INDEX idx_questions_category ON questions(category_id, is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_questions_difficulty ON questions(difficulty) INCLUDE (category_id);
CREATE INDEX idx_question_choices_correct ON question_choices(question_id) WHERE is_correct = TRUE;
CREATE INDEX idx_question_tags_tag ON question_tags(tag_id); 