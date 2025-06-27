from flask import Blueprint, request, jsonify, session
from models.user_model import User
from security.passwords import hash_password, verify_password
import re
from functools import wraps
import secrets
from datetime import datetime

user_bp = Blueprint("user", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    return True, None

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

@user_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        # Validation
        if not username or len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters long"}), 400
        
        if not email or not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return jsonify({"error": password_error}), 400

        if User.find_by_username(username):
            return jsonify({"error": "Username already exists"}), 400

        if User.find_by_email(email):
            return jsonify({"error": "Email already registered"}), 400

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role='user'
        )
        user.save()

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201

    except Exception as e:
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@user_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = User.find_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

        # Create session
        session_token = secrets.token_urlsafe(32)
        session_data = User.create_session(
            user.id,
            session_token,
            request.remote_addr,
            request.user_agent.string
        )

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["session_token"] = session_token

        return jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
            "session": session_data
        })

    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    try:
        user = User.find_by_id(session["user_id"])
        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404

        # Get user stats and achievements
        stats = user.get_stats()
        achievements = user.get_achievements()
        
        return jsonify({
            "user": user.to_dict(),
            "stats": stats,
            "achievements": achievements
        })

    except Exception as e:
        return jsonify({"error": "Failed to fetch profile", "details": str(e)}), 500

@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user = User.find_by_id(session["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

        update_data = {}

        # Validate and prepare user data updates
        if "email" in data:
            new_email = data["email"].strip()
            if not validate_email(new_email):
                return jsonify({"error": "Invalid email format"}), 400
            if User.find_by_email(new_email) and new_email != user.email:
                return jsonify({"error": "Email already registered"}), 400
            update_data["email"] = new_email

        if "password" in data:
            is_valid_password, password_error = validate_password(data["password"])
            if not is_valid_password:
                return jsonify({"error": password_error}), 400
            update_data["password_hash"] = hash_password(data["password"])

        # Prepare profile data updates
        profile_fields = ["display_name", "avatar_url", "bio", "country", "timezone", "preferences"]
        for field in profile_fields:
            if field in data:
                update_data[field] = data[field]

        user.update(update_data)
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict()
        })

    except Exception as e:
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500

@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        if "session_token" in session:
            User.end_session(session["session_token"])
        session.clear()
        return jsonify({"message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"error": "Logout failed", "details": str(e)}), 500

@user_bp.route("/me/stats", methods=["GET"])
@login_required
def get_user_stats():
    try:
        user = User.find_by_id(session["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

        stats = user.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": "Failed to fetch stats", "details": str(e)}), 500

@user_bp.route("/me/achievements", methods=["GET"])
@login_required
def get_user_achievements():
    try:
        user = User.find_by_id(session["user_id"])
        if not user:
            return jsonify({"error": "User not found"}), 404

        achievements = user.get_achievements()
        return jsonify(achievements)
    except Exception as e:
        return jsonify({"error": "Failed to fetch achievements", "details": str(e)}), 500

@user_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get global leaderboard"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        leaderboard = UserStats.get_leaderboard(limit)
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": "Failed to fetch leaderboard", "details": str(e)}), 500

@user_bp.route("/me/progress", methods=["GET"])
@login_required
def user_progress():
    """Get user's progress and milestones"""
    try:
        stats = UserStats.get(session['user_id'])
        if not stats:
            return jsonify({"error": "Stats not found"}), 404
            
        # Calculate progress towards next milestones
        next_milestones = {
            "games": (stats.games_played // 10 + 1) * 10,
            "wins": (stats.wins // 5 + 1) * 5,
            "perfect_games": stats.perfect_games + 1,
            "rank_points": (stats.rank_points // 100 + 1) * 100,
            "xp_level": (stats.xp // 1000 + 1)
        }
        
        progress = {
            "current_level": stats.xp // 1000,
            "xp_progress": stats.xp % 1000,
            "next_level_xp": 1000,
            "milestones": {
                "games": {
                    "current": stats.games_played,
                    "next": next_milestones["games"],
                    "progress": (stats.games_played / next_milestones["games"]) * 100
                },
                "wins": {
                    "current": stats.wins,
                    "next": next_milestones["wins"],
                    "progress": (stats.wins / next_milestones["wins"]) * 100
                },
                "perfect_games": {
                    "current": stats.perfect_games,
                    "next": next_milestones["perfect_games"],
                    "progress": 100 if stats.perfect_games > 0 else 0
                },
                "rank": {
                    "current": stats.rank_points,
                    "next": next_milestones["rank_points"],
                    "progress": (stats.rank_points / next_milestones["rank_points"]) * 100
                }
            }
        }
        
        return jsonify(progress)
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch progress", "details": str(e)}), 500