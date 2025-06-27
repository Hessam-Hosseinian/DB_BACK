-- Question Management Queries
-- ================================

-- Get questions by category with choices
SELECT q.*,
       c.name as category_name,
       json_agg(json_build_object(
           'id', qc.id,
           'text', qc.choice_text,
           'position', qc.position,
           'is_correct', qc.is_correct,
           'explanation', qc.explanation
       )) as choices,
       array_agg(DISTINCT t.name) as tags
FROM questions q
JOIN categories c ON q.category_id = c.id
LEFT JOIN question_choices qc ON q.id = qc.question_id
LEFT JOIN question_tags qt ON q.id = qt.question_id
LEFT JOIN tags t ON qt.tag_id = t.id
WHERE q.category_id = $1 AND q.is_verified = true
GROUP BY q.id, c.name;

-- Get random questions for a game
WITH category_questions AS (
    SELECT q.id
    FROM questions q
    WHERE q.category_id = ANY($1::int[])
    AND q.difficulty = $2
    AND q.is_verified = true
    ORDER BY RANDOM()
    LIMIT $3
)
SELECT q.*,
       json_agg(json_build_object(
           'id', qc.id,
           'text', qc.choice_text,
           'position', qc.position
       )) as choices
FROM category_questions cq
JOIN questions q ON cq.id = q.id
JOIN question_choices qc ON q.id = qc.question_id
GROUP BY q.id;

-- Create new question with choices
WITH new_question AS (
    INSERT INTO questions (text, category_id, difficulty, created_by)
    VALUES ($1, $2, $3, $4)
    RETURNING id
),
choices AS (
    INSERT INTO question_choices (question_id, choice_text, is_correct, position, explanation)
    SELECT nq.id, c->>'text', (c->>'is_correct')::boolean, c->>'position', c->>'explanation'
    FROM new_question nq
    CROSS JOIN json_array_elements($5::json) as c
    RETURNING *
)
SELECT q.*, json_agg(c.*) as choices
FROM new_question nq
JOIN questions q ON nq.id = q.id
LEFT JOIN choices c ON q.id = c.question_id
GROUP BY q.id;

-- Report question
INSERT INTO question_reports (question_id, user_id, reason)
VALUES ($1, $2, $3)
RETURNING *;

-- Get question statistics
SELECT q.id,
       q.text,
       q.times_used,
       q.success_rate,
       COUNT(DISTINCT ra.user_id) as unique_users_attempted,
       COUNT(ra.id) as total_attempts,
       COUNT(CASE WHEN ra.is_correct THEN 1 END) as correct_attempts,
       ROUND(AVG(ra.response_time_ms)::numeric, 2) as avg_response_time
FROM questions q
LEFT JOIN game_rounds gr ON q.id = gr.question_id
LEFT JOIN round_answers ra ON gr.id = ra.round_id
WHERE q.id = $1
GROUP BY q.id;

-- Search questions by tags
SELECT DISTINCT q.*,
       array_agg(DISTINCT t.name) as matching_tags
FROM questions q
JOIN question_tags qt ON q.id = qt.question_id
JOIN tags t ON qt.tag_id = t.id
WHERE t.name = ANY($1::varchar[])
GROUP BY q.id
HAVING COUNT(DISTINCT t.name) >= $2;

-- Update question verification status
UPDATE questions
SET is_verified = $2,
    success_rate = COALESCE(
        (SELECT ROUND(COUNT(CASE WHEN ra.is_correct THEN 1 END)::numeric / NULLIF(COUNT(*), 0) * 100, 2)
         FROM game_rounds gr
         JOIN round_answers ra ON gr.id = ra.round_id
         WHERE gr.question_id = questions.id),
        0
    )
WHERE id = $1
RETURNING *; 