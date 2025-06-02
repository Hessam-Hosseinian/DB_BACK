--:create_games
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'active', 'finished'
    winner_id INTEGER,                      -- NULL تا زمان پایان بازی
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,

    FOREIGN KEY (player1_id) REFERENCES users(id),
    FOREIGN KEY (player2_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);

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

    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

--:insert_game
INSERT INTO games (player1_id, player2_id, status)
VALUES (%s, %s, %s) RETURNING id;

--:insert_round
INSERT INTO rounds (game_id, round_number, question_id)
VALUES (%s, %s, %s) RETURNING id;
