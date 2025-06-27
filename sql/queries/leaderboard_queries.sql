-- Leaderboard and Statistics Queries
-- ================================

-- Get global leaderboard
SELECT u.username,
       us.total_points,
       us.games_played,
       us.games_won,
       ROUND(us.games_won::numeric / NULLIF(us.games_played, 0) * 100, 2) as win_rate,
       ROUND(us.correct_answers::numeric / NULLIF(us.total_answers, 0) * 100, 2) as accuracy,
       RANK() OVER (ORDER BY us.total_points DESC) as rank
FROM user_stats us
JOIN users u ON us.user_id = u.id
WHERE us.games_played > 0
LIMIT $1;

-- Get category leaderboard
SELECT u.username,
       ucs.total_points,
       ucs.games_played,
       ucs.correct_answers,
       ROUND(ucs.correct_answers::numeric / NULLIF(ucs.total_answers, 0) * 100, 2) as accuracy,
       RANK() OVER (ORDER BY ucs.total_points DESC) as rank
FROM user_category_stats ucs
JOIN users u ON ucs.user_id = u.id
WHERE ucs.category_id = $1 AND ucs.games_played > 0
LIMIT $2;

-- Get daily leaderboard
SELECT u.username,
       l.score,
       l.rank
FROM leaderboards l
JOIN users u ON l.user_id = u.id
WHERE l.scope = 'daily'
  AND DATE(l.generated_at) = CURRENT_DATE
  AND (l.category_id = $1 OR $1 IS NULL)
ORDER BY l.rank
LIMIT $2;

-- Get user ranking history
SELECT u.username,
       l.scope,
       l.score,
       l.rank,
       c.name as category_name,
       l.generated_at
FROM leaderboards l
JOIN users u ON l.user_id = u.id
LEFT JOIN categories c ON l.category_id = c.id
WHERE l.user_id = $1
ORDER BY l.generated_at DESC
LIMIT $2;

-- Get category statistics
SELECT c.name as category_name,
       COUNT(DISTINCT q.id) as total_questions,
       COUNT(DISTINCT gr.id) as times_played,
       ROUND(AVG(q.success_rate), 2) as avg_success_rate,
       COUNT(DISTINCT gp.user_id) as unique_players
FROM categories c
LEFT JOIN questions q ON c.id = q.category_id
LEFT JOIN game_rounds gr ON q.id = gr.question_id
LEFT JOIN round_answers ra ON gr.id = ra.round_id
LEFT JOIN game_participants gp ON ra.user_id = gp.user_id
GROUP BY c.id, c.name;

-- Refresh daily leaderboard
WITH daily_scores AS (
    SELECT gp.user_id,
           COALESCE(g.category_id, 0) as category_id,
           SUM(gp.score) as daily_score,
           RANK() OVER (PARTITION BY COALESCE(g.category_id, 0) 
                       ORDER BY SUM(gp.score) DESC) as daily_rank
    FROM game_participants gp
    JOIN games g ON gp.game_id = g.id
    WHERE DATE(g.end_time) = CURRENT_DATE
    GROUP BY gp.user_id, COALESCE(g.category_id, 0)
)
INSERT INTO leaderboards (user_id, scope, category_id, rank, score)
SELECT user_id, 'daily', 
       NULLIF(category_id, 0),
       daily_rank,
       daily_score
FROM daily_scores
ON CONFLICT (user_id, scope, COALESCE(category_id, -1))
DO UPDATE SET rank = EXCLUDED.rank,
              score = EXCLUDED.score,
              generated_at = NOW(); 