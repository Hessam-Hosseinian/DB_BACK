--:create_questions
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL UNIQUE,
    choice_a TEXT NOT NULL,
    choice_b TEXT NOT NULL,
    choice_c TEXT NOT NULL,
    choice_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    category_id INTEGER NOT NULL,
    difficulty TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);


--:insert_question
INSERT INTO questions (
    text, choice_a, choice_b, choice_c, choice_d,
    correct_answer, category_id, difficulty
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
