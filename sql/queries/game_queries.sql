-- Game Related Queries
-- ================================

-- Create new game
WITH new_game AS (
    INSERT INTO games (game_type_id, game_config)
    VALUES ($1, $2::jsonb)
    RETURNING id, game_type_id
)
INSERT INTO game_participants (game_id, user_id)
SELECT new_game.id, unnest($3::bigint[])
FROM new_game
RETURNING game_id;

-- Get active game details with participants
SELECT g.*, 
       gt.name as game_type_name,
       json_agg(json_build_object(
           'user_id', u.id,
           'username', u.username,
           'score', gp.score,
           'status', gp.status
       )) as participants
FROM games g
JOIN game_types gt ON g.game_type_id = gt.id
JOIN game_participants gp ON g.id = gp.game_id
JOIN users u ON gp.user_id = u.id
WHERE g.id = $1
GROUP BY g.id, gt.name;

-- Get current game round with question
SELECT gr.*,
       q.text as question_text,
       q.difficulty,
       json_agg(json_build_object(
           'id', qc.id,
           'text', qc.choice_text,
           'position', qc.position
       )) as choices
FROM game_rounds gr
JOIN questions q ON gr.question_id = q.id
JOIN question_choices qc ON q.id = qc.question_id
WHERE gr.game_id = $1 AND gr.status = 'active'
GROUP BY gr.id, q.text, q.difficulty;

-- Submit answer for current round
WITH answer_submission AS (
    INSERT INTO round_answers (round_id, user_id, choice_id, response_time_ms)
    VALUES ($1, $2, $3, $4)
    RETURNING *
),
score_update AS (
    UPDATE game_participants
    SET score = score + (
        SELECT points_earned 
        FROM answer_submission 
        WHERE is_correct = true
    )
    WHERE game_id = (
        SELECT game_id 
        FROM game_rounds 
        WHERE id = $1
    )
    AND user_id = $2
)
SELECT * FROM answer_submission;

-- Get game leaderboard
SELECT u.username,
       gp.score,
       COUNT(ra.id) as questions_answered,
       COUNT(CASE WHEN ra.is_correct THEN 1 END) as correct_answers,
       ROUND(AVG(ra.response_time_ms)::numeric, 2) as avg_response_time
FROM game_participants gp
JOIN users u ON gp.user_id = u.id
LEFT JOIN game_rounds gr ON gp.game_id = gr.game_id
LEFT JOIN round_answers ra ON gr.id = ra.round_id AND ra.user_id = gp.user_id
WHERE gp.game_id = $1
GROUP BY u.username, gp.score
ORDER BY gp.score DESC;

-- End game and update stats
WITH game_summary AS (
    SELECT game_id,
           user_id,
           score,
           COUNT(ra.id) as total_answers,
           COUNT(CASE WHEN ra.is_correct THEN 1 END) as correct_answers
    FROM game_participants gp
    LEFT JOIN game_rounds gr ON gp.game_id = gr.game_id
    LEFT JOIN round_answers ra ON gr.id = ra.round_id AND ra.user_id = gp.user_id
    WHERE gp.game_id = $1
    GROUP BY game_id, user_id, score
)
UPDATE user_stats us
SET games_played = games_played + 1,
    games_won = games_won + CASE WHEN gs.score = (
        SELECT MAX(score) FROM game_summary WHERE game_id = $1
    ) THEN 1 ELSE 0 END,
    total_points = total_points + gs.score,
    total_answers = total_answers + gs.total_answers,
    correct_answers = correct_answers + gs.correct_answers,
    last_played_at = NOW()
FROM game_summary gs
WHERE us.user_id = gs.user_id; 