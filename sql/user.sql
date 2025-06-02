--:create_users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
    CONSTRAINT username_length CHECK (length(username) >= 3),
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

--:insert_user
INSERT INTO users (username, email, password, registered_at, is_admin)
VALUES (%s, %s, %s, %s, %s)
RETURNING id;

--:update_user
UPDATE users 
SET email = %s,
    password = %s,
    is_admin = %s
WHERE id = %s;

--:delete_user
DELETE FROM users WHERE id = %s;

--:get_user_by_id
SELECT id, username, email, password, registered_at, is_admin
FROM users 
WHERE id = %s AND status = 'active';

--:get_user_by_username
SELECT id, username, email, password, registered_at, is_admin
FROM users 
WHERE username = %s AND status = 'active';

--:get_user_by_email
SELECT id, username, email, password, registered_at, is_admin
FROM users 
WHERE email = %s AND status = 'active';

--:get_random_opponent
SELECT id, username, email, password, registered_at, is_admin
FROM users 
WHERE id != %s 
  AND status = 'active'
ORDER BY RANDOM() 
LIMIT 1;

--:get_leaderboard
SELECT 
    u.id,
    u.username,
    COUNT(CASE WHEN g.winner_id = u.id THEN 1 END) as wins,
    COUNT(g.id) as games_played
FROM users u
LEFT JOIN games g ON u.id = g.player1_id OR u.id = g.player2_id
WHERE u.status = 'active'
GROUP BY u.id, u.username
ORDER BY wins DESC, games_played ASC
LIMIT %s;

--:update_last_login
UPDATE users 
SET last_login = CURRENT_TIMESTAMP 
WHERE id = %s;

--:update_user_status
UPDATE users 
SET status = %s 
WHERE id = %s;

--:get_active_users_count
SELECT COUNT(*) 
FROM users 
WHERE status = 'active';

--:get_users_by_registration_date
SELECT id, username, email, registered_at, is_admin
FROM users
WHERE registered_at >= %s 
  AND registered_at < %s
  AND status = 'active'
ORDER BY registered_at DESC;
