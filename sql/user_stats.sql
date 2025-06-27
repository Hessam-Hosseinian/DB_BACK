-- Get user stats
-- name: get_user_stats
SELECT 
    games_played,
    wins,
    losses,
    draws,
    correct_answers,
    total_answers,
    total_points,
    total_bonus_points,
    fastest_answer,
    average_answer_time,
    longest_win_streak,
    current_win_streak,
    perfect_games,
    xp,
    rank_points,
    last_updated
FROM user_stats
WHERE user_id = $1;

-- Initialize user stats
-- name: init_user_stats
INSERT INTO user_stats (
    user_id, games_played, wins, losses, draws,
    correct_answers, total_answers, total_points,
    total_bonus_points, fastest_answer, average_answer_time,
    longest_win_streak, current_win_streak, perfect_games,
    xp, rank_points, last_updated
) VALUES (
    $1, 0, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, 0, 0, 0, 0, 0, NOW()
) ON CONFLICT (user_id) DO NOTHING;

-- Increment game count
-- name: increment_game
UPDATE user_stats
SET games_played = games_played + 1,
    last_updated = NOW()
WHERE user_id = $1;

-- Increment win count
-- name: increment_win
UPDATE user_stats
SET wins = wins + 1,
    current_win_streak = current_win_streak + 1,
    longest_win_streak = GREATEST(longest_win_streak, current_win_streak + 1),
    last_updated = NOW()
WHERE user_id = $1;

-- Increment loss count
-- name: increment_loss
UPDATE user_stats
SET losses = losses + 1,
    current_win_streak = 0,
    last_updated = NOW()
WHERE user_id = $1;

-- Increment draw count
-- name: increment_draw
UPDATE user_stats
SET draws = draws + 1,
    last_updated = NOW()
WHERE user_id = $1;

-- Update answer stats
-- name: update_answer_stats
UPDATE user_stats
SET correct_answers = correct_answers + $1,
    total_answers = total_answers + 1,
    total_points = total_points + $2,
    total_bonus_points = total_bonus_points + $3,
    fastest_answer = CASE 
        WHEN fastest_answer IS NULL THEN $4
        ELSE LEAST(fastest_answer, $4)
    END,
    average_answer_time = CASE 
        WHEN average_answer_time IS NULL THEN $5
        ELSE (average_answer_time * total_answers + $6) / (total_answers + 1)
    END,
    xp = xp + $8,
    last_updated = NOW()
WHERE user_id = $9;

-- Record perfect game
-- name: record_perfect_game
UPDATE user_stats
SET perfect_games = perfect_games + 1,
    last_updated = NOW()
WHERE user_id = $1;

-- Get leaderboard
-- name: get_leaderboard
SELECT 
    u.username,
    s.rank_points,
    s.wins,
    s.games_played,
    s.perfect_games,
    s.xp,
    CASE 
        WHEN s.total_answers > 0 THEN 
            ROUND((s.correct_answers::float / s.total_answers::float) * 100, 2)
        ELSE 0 
    END as accuracy,
    s.fastest_answer,
    s.longest_win_streak
FROM user_stats s
JOIN users u ON s.user_id = u.id
ORDER BY s.rank_points DESC, s.wins DESC
LIMIT $1;

-- Get user rank
-- name: get_user_rank
SELECT COUNT(*) + 1
FROM user_stats
WHERE rank_points > (
    SELECT rank_points
    FROM user_stats
    WHERE user_id = $1
); 