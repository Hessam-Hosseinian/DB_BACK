--:create_users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
);

--:insert_user
INSERT INTO users (username, email, password)
VALUES (%s, %s, %s) RETURNING id;

--:get_user_by_id
SELECT id, username, email, password, registered_at, is_admin
FROM users WHERE id = %s;

--:get_user_by_username
SELECT id, username, email, password, registered_at, is_admin
FROM users WHERE username = %s;
