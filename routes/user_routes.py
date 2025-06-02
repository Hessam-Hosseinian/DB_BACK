from flask import Blueprint, request, jsonify, session
from models.user_model import User
from models.user_stats_model import UserStats
from security.passwords import hash_password, verify_password

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.find_by_username(username):
        return jsonify({"error": "Username already exists"}), 400

    hashed_pw = hash_password(password)
    user = User(username=username, email=email, password=hashed_pw)
    user.save()

    return jsonify({"message": "User registered", "user_id": user.id})

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.find_by_username(username)
    if not user or not verify_password(password, user.password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    session["username"] = user.username

    return jsonify({"message": "Login successful", "user_id": user.id})


@user_bp.route("/profile", methods=["GET"])
def profile():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "user_id": session["user_id"],
        "username": session["username"]
    })



@user_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@user_bp.route("/me/stats", methods=["GET"])
def user_stats():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    user_id = session["user_id"]
    stats = UserStats.get(user_id)
    if not stats:
        return jsonify({"error": "Stats not found"}), 404

    accuracy = round((stats.correct_answers / stats.total_answers) * 100, 2) if stats.total_answers else 0

    return jsonify({
        "games_played": stats.games_played,
        "wins": stats.wins,
        "correct_answers": stats.correct_answers,
        "total_answers": stats.total_answers,
        "accuracy_percent": accuracy,
        "xp": stats.xp
    })