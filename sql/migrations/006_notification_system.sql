-- Notification System Tables
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
);

-- Indexes
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_type ON notifications(type_id, created_at DESC); 