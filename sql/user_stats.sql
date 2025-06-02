--:create_user_stats
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_answers INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

--:init_user_stats
INSERT INTO user_stats (user_id) VALUES (%s);

--:increment_game
UPDATE user_stats SET games_played = games_played + 1 WHERE user_id = %s;

--:increment_win
UPDATE user_stats SET wins = wins + 1 WHERE user_id = %s;

--:increment_answer
UPDATE user_stats
SET
    total_answers = total_answers + 1,
    correct_answers = correct_answers + %s,
    xp = xp + %s
WHERE user_id = %s;

--:get_user_stats
SELECT games_played, wins, correct_answers, total_answers, xp
FROM user_stats WHERE user_id = %s;
