import random

from flask import Blueprint, request, jsonify, session

from db.connection import get_connection
from models.game_model import Game
from models.round_model import Round
from models.user_model import User
from models.question_model import Question
from models.matchmaking import Matchmaking


game_bp = Blueprint("game", __name__)

@game_bp.route("/games/start", methods=["POST"])
def start_game():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    player_id = session["user_id"]
    opponent_id = Matchmaking.find_waiting_player(exclude_user_id=player_id)

    if opponent_id:
        Matchmaking.remove(opponent_id)

        game = Game(player1_id=opponent_id, player2_id=player_id, status="active")
        game.save()

        chooser_id = opponent_id  # Round 1 chooser
        round1 = Round(game_id=game.id, round_number=1, chooser_id=chooser_id)
        round1.save()

        return jsonify({
            "message": "Game matched",
            "game_id": game.id,
            "opponent_id": opponent_id,
            "round_id": round1.id,
            "your_turn_to_choose": player_id == chooser_id
        })

    else:
        Matchmaking.add(player_id)
        return jsonify({"message": "Waiting for an opponent"})


@game_bp.route("/games/<int:game_id>/rounds/<int:round_id>/choose_category", methods=["POST"])
def choose_category(game_id, round_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    data = request.get_json()
    chosen_category = data.get("category")

    round_obj = Round.get_by_id(round_id)
    if not round_obj:
        return jsonify({"error": "Round not found"}), 404

    if user_id != round_obj.chooser_id:
        return jsonify({"error": "Not your turn to choose category"}), 403

    if round_obj.category:
        return jsonify({"error": "Category already chosen"}), 400

    questions = Question.get_3_random_by_category(chosen_category)
    if len(questions) < 3:
        return jsonify({"error": "Not enough questions in category"}), 500

    round_obj.set_category_and_questions(chosen_category, questions)

    # ساخت راند بعدی در صورت نیاز
    if round_obj.round_number < 5:
        next_round_number = round_obj.round_number + 1
        game = round_obj.get_game()
        next_chooser = game.player1_id if round_obj.chooser_id == game.player2_id else game.player2_id

        new_round = Round(
            game_id=game.id,
            round_number=next_round_number,
            chooser_id=next_chooser
        )
        new_round.save()

    return jsonify({
        "message": "Category set",
        "category": chosen_category,
        "questions": [
            {"id": q.id, "text": q.text, "choices": q.choices}
            for q in questions
        ]
    })



@game_bp.route("/games/<int:game_id>/answer", methods=["POST"])
def submit_answer(game_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()
    round_id = data.get("round_id")
    answer = data.get("answer")
    question_number = data.get("question_number")
    user_id = session["user_id"]

    round_obj = Round.get_by_id(round_id)
    if not round_obj:
        return jsonify({"error": "Round not found"}), 404

    game = round_obj.get_game()
    if not game or user_id not in [game.player1_id, game.player2_id]:
        return jsonify({"error": "Access denied to this game"}), 403

    if round_obj.has_answered(user_id, question_number):
        return jsonify({"error": "Already answered this question"}), 400

    correct_answer = round_obj.get_correct_answer(question_number)
    is_correct = (answer == correct_answer)
    round_obj.save_answer(user_id, question_number, answer, is_correct)

    # بررسی پایان بازی
    TOTAL_ROUNDS = 5
    QUESTIONS_PER_ROUND = 3
    REQUIRED_ANSWERS = TOTAL_ROUNDS * QUESTIONS_PER_ROUND

    player1_answers = Round.count_total_answers(game.id, game.player1_id)
    player2_answers = Round.count_total_answers(game.id, game.player2_id)

    if player1_answers >= REQUIRED_ANSWERS and player2_answers >= REQUIRED_ANSWERS:
        player1_score = Round.total_correct_answers(game.id, game.player1_id)
        player2_score = Round.total_correct_answers(game.id, game.player2_id)

        game.status = "finished"
        if player1_score > player2_score:
            game.winner_id = game.player1_id
        elif player2_score > player1_score:
            game.winner_id = game.player2_id
        else:
            game.winner_id = None  # مساوی

        game.save()

    return jsonify({
        "message": "Answer submitted",
        "correct": is_correct
    })


@game_bp.route("/games/<int:game_id>/status", methods=["GET"])
def game_status(game_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    game = Game.find_by_id(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    if user_id not in [game.player1_id, game.player2_id]:
        return jsonify({"error": "Access denied to this game"}), 403

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            SUM(CASE WHEN player1_correct THEN 1 ELSE 0 END),
            SUM(CASE WHEN player2_correct THEN 1 ELSE 0 END)
        FROM rounds
        WHERE game_id = %s
    """, (game.id,))
    scores = cur.fetchone()
    cur.close()
    conn.close()

    player1_score = scores[0] or 0
    player2_score = scores[1] or 0

    return jsonify({
        "game_id": game.id,
        "player1_id": game.player1_id,
        "player2_id": game.player2_id,
        "player1_score": player1_score,
        "player2_score": player2_score,
        "status": game.status,
        "winner_id": game.winner_id
    })
@game_bp.route("/games/<int:game_id>/active_round", methods=["GET"])
def get_active_round(game_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    user_id = session["user_id"]

    game = Game.find_by_id(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if user_id not in [game.player1_id, game.player2_id]:
        return jsonify({"error": "Access denied"}), 403

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, round_number, chooser_id, category
        FROM rounds
        WHERE game_id = %s
        ORDER BY round_number DESC
        LIMIT 1
    """, (game_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "No round found"}), 404

    round_info = {
        "round_id": row[0],
        "round_number": row[1],
        "chooser_id": row[2],
        "category": row[3],
        "your_turn_to_choose": (row[3] is None and row[2] == user_id)
    }

    return jsonify(round_info)


@game_bp.route("/games/<int:game_id>/rounds/<int:round_id>/details", methods=["GET"])
def round_details(game_id, round_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    user_id = session["user_id"]

    game = Game.find_by_id(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if user_id not in [game.player1_id, game.player2_id]:
        return jsonify({"error": "Access denied to this game"}), 403

    round_obj = Round.get_by_id(round_id)
    if not round_obj or round_obj.game_id != game_id:
        return jsonify({"error": "Round not found"}), 404

    conn = get_connection()
    cur = conn.cursor()

    # گرفتن سوالات این راند
    cur.execute("""
        SELECT rq.question_number, q.id, q.text, q.choices
        FROM round_questions rq
        JOIN questions q ON rq.question_id = q.id
        WHERE rq.round_id = %s
        ORDER BY rq.question_number ASC
    """, (round_id,))
    question_rows = cur.fetchall()

    # گرفتن پاسخ‌ها برای هر بازیکن
    cur.execute("""
        SELECT user_id, question_number, answer, is_correct
        FROM round_answers
        WHERE round_id = %s
    """, (round_id,))
    answer_rows = cur.fetchall()

    cur.close()
    conn.close()

    # ساخت دیکشنری پاسخ‌ها: {user_id: {question_number: {answer, correct}}}
    answers = {}
    for user in [game.player1_id, game.player2_id]:
        answers[user] = {}

    for row in answer_rows:
        uid, qn, ans, correct = row
        answers[uid][qn] = {
            "answer": ans,
            "is_correct": correct
        }

    questions = []
    for qn, qid, text, choices in question_rows:
        questions.append({
            "question_number": qn,
            "question_id": qid,
            "text": text,
            "choices": choices,
            "player1_answer": answers[game.player1_id].get(qn),
            "player2_answer": answers[game.player2_id].get(qn)
        })

    return jsonify({
        "round_id": round_obj.id,
        "round_number": round_obj.round_number,
        "chooser_id": round_obj.chooser_id,
        "category": round_obj.category,
        "questions": questions
    })
@game_bp.route("/games/<int:game_id>/summary", methods=["GET"])
def game_summary(game_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    user_id = session["user_id"]

    game = Game.find_by_id(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    if user_id not in [game.player1_id, game.player2_id]:
        return jsonify({"error": "Access denied to this game"}), 403

    conn = get_connection()
    cur = conn.cursor()

    # گرفتن راندها
    cur.execute("""
        SELECT id, round_number, chooser_id, category
        FROM rounds
        WHERE game_id = %s
        ORDER BY round_number ASC
    """, (game_id,))
    round_rows = cur.fetchall()

    # گرفتن همه سوالات بازی
    cur.execute("""
        SELECT rq.round_id, rq.question_number, q.id, q.text, q.choices
        FROM round_questions rq
        JOIN questions q ON rq.question_id = q.id
        WHERE rq.round_id IN (
            SELECT id FROM rounds WHERE game_id = %s
        )
    """, (game_id,))
    question_rows = cur.fetchall()

    # گرفتن پاسخ‌ها
    cur.execute("""
        SELECT round_id, user_id, question_number, answer, is_correct
        FROM round_answers
        WHERE round_id IN (
            SELECT id FROM rounds WHERE game_id = %s
        )
    """, (game_id,))
    answer_rows = cur.fetchall()

    cur.close()
    conn.close()

    # ساخت دیکشنری‌ها
    answers_by_user = {game.player1_id: {}, game.player2_id: {}}
    for r in answer_rows:
        rid, uid, qn, ans, correct = r
        answers_by_user[uid].setdefault(rid, {})[qn] = {"answer": ans, "is_correct": correct}

    questions_by_round = {}
    for r in question_rows:
        rid, qn, qid, text, choices = r
        questions_by_round.setdefault(rid, []).append({
            "question_number": qn,
            "question_id": qid,
            "text": text,
            "choices": choices
        })

    # ساخت راندها با پاسخ‌ها
    rounds = []
    for rid, rn, chooser_id, category in round_rows:
        qlist = questions_by_round.get(rid, [])
        for q in qlist:
            qn = q["question_number"]
            q["player1_answer"] = answers_by_user[game.player1_id].get(rid, {}).get(qn)
            q["player2_answer"] = answers_by_user[game.player2_id].get(rid, {}).get(qn)

        rounds.append({
            "round_id": rid,
            "round_number": rn,
            "chooser_id": chooser_id,
            "category": category,
            "questions": sorted(qlist, key=lambda q: q["question_number"])
        })

    return jsonify({
        "game_id": game.id,
        "player1_id": game.player1_id,
        "player2_id": game.player2_id,
        "status": game.status,
        "winner_id": game.winner_id,
        "rounds": rounds
    })
@game_bp.route("/notifications", methods=["GET"])
def get_notifications():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, game_id, type, message, created_at
        FROM notifications
        WHERE user_id = %s AND seen = FALSE
        ORDER BY created_at ASC
    """, (user_id,))
    notifs = cur.fetchall()

    notif_ids = [row[0] for row in notifs]
    if notif_ids:
        cur.execute("UPDATE notifications SET seen = TRUE WHERE id = ANY(%s)", (notif_ids,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify([
        {
            "game_id": row[1],
            "type": row[2],
            "message": row[3],
            "timestamp": row[4].isoformat()
        } for row in notifs
    ])
@game_bp.route("/users/me/stats", methods=["GET"])
def user_stats():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) FROM games WHERE winner_id = %s
    """, (user_id,))
    wins = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM games WHERE player1_id = %s OR player2_id = %s
    """, (user_id, user_id))
    total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM round_answers
        WHERE user_id = %s AND is_correct = TRUE
    """, (user_id,))
    correct_answers = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        "games_played": total,
        "games_won": wins,
        "correct_answers": correct_answers
    })
@game_bp.route("/users/me/stats", methods=["GET"])
def user_stats():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    # تعداد بازی‌هایی که کاربر در آن شرکت کرده
    cur.execute("""
        SELECT COUNT(*) FROM games
        WHERE player1_id = %s OR player2_id = %s
    """, (user_id, user_id))
    total_games = cur.fetchone()[0]

    # تعداد بردها
    cur.execute("""
        SELECT COUNT(*) FROM games
        WHERE winner_id = %s
    """, (user_id,))
    wins = cur.fetchone()[0]

    # تعداد مساوی‌ها
    cur.execute("""
        SELECT COUNT(*) FROM games
        WHERE (player1_id = %s OR player2_id = %s) AND winner_id IS NULL AND status = 'finished'
    """, (user_id, user_id))
    draws = cur.fetchone()[0]

    # تعداد باخت‌ها = کل - برد - مساوی
    losses = total_games - wins - draws

    # تعداد پاسخ‌ها
    cur.execute("""
        SELECT COUNT(*) FROM round_answers
        WHERE user_id = %s
    """, (user_id,))
    total_answers = cur.fetchone()[0]

    # تعداد پاسخ‌های صحیح
    cur.execute("""
        SELECT COUNT(*) FROM round_answers
        WHERE user_id = %s AND is_correct = TRUE
    """, (user_id,))
    correct_answers = cur.fetchone()[0]

    cur.close()
    conn.close()

    accuracy = (correct_answers / total_answers) * 100 if total_answers > 0 else 0.0

    return jsonify({
        "games_played": total_games,
        "games_won": wins,
        "games_lost": losses,
        "games_drawn": draws,
        "total_answers": total_answers,
        "correct_answers": correct_answers,
        "accuracy_percent": round(accuracy, 2)
    })
