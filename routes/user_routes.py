from flask import Blueprint, request, jsonify, session
from models.user_model import User
from models.user_stats_model import UserStats
from security.passwords import hash_password, verify_password
import re
from functools import wraps

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

        hashed_pw = hash_password(password)
        user = User(username=username, email=email, password=hashed_pw)
        user.save()

        # Initialize user stats
        UserStats.init_for_user(user.id)

        return jsonify({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": username
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
        if not user or not verify_password(password, user.password):
            return jsonify({"error": "Invalid credentials"}), 401

        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["is_admin"] = user.is_admin

        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        })

    except Exception as e:
        return jsonify({"error": "Login failed", "details": str(e)}), 500

@user_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    try:
        user = User.find_by_id(session["user_id"])
        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404

        # stats = UserStats.get(user.id)
        
        return jsonify({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "registered_at": user.registered_at.isoformat() if user.registered_at else None,
            "is_admin": user.is_admin,
            # "stats": stats.to_dict() if stats else None
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

        if "email" in data:
            new_email = data["email"].strip()
            if not validate_email(new_email):
                return jsonify({"error": "Invalid email format"}), 400
            if User.find_by_email(new_email) and new_email != user.email:
                return jsonify({"error": "Email already registered"}), 400
            user.email = new_email

        if "password" in data:
            is_valid_password, password_error = validate_password(data["password"])
            if not is_valid_password:
                return jsonify({"error": password_error}), 400
            user.password = hash_password(data["password"])

        user.update()
        return jsonify({"message": "Profile updated successfully"})

    except Exception as e:
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500

@user_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@user_bp.route("/me/stats", methods=["GET"])
@login_required
def user_stats():
    """Get detailed user statistics"""
    try:
        user_id = session["user_id"]
        stats = UserStats.get(user_id)
        if not stats:
            return jsonify({"error": "Stats not found"}), 404

        # Get user's rank
        rank = stats.get_rank()
        
        response = stats.to_dict()
        response['rank'] = rank
        
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": "Failed to fetch stats", "details": str(e)}), 500

@user_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get global leaderboard"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        leaderboard = UserStats.get_leaderboard(limit)
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": "Failed to fetch leaderboard", "details": str(e)}), 500

@user_bp.route("/me/achievements", methods=["GET"])
@login_required
def user_achievements():
    """Get user's achievements"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                a.name,
                a.description,
                a.points,
                pa.earned_at,
                g.game_type,
                g.player1_score,
                g.player2_score
            FROM player_achievements pa
            JOIN achievements a ON pa.achievement_id = a.id
            LEFT JOIN games g ON pa.game_id = g.id
            WHERE pa.player_id = %s
            ORDER BY pa.earned_at DESC
        """, (session['user_id'],))
        
        achievements = [
            {
                "name": row[0],
                "description": row[1],
                "points": row[2],
                "earned_at": row[3].isoformat(),
                "game_info": {
                    "type": row[4],
                    "score": row[5] if row[5] else row[6]
                } if row[4] else None
            }
            for row in cur.fetchall()
        ]
        
        return jsonify(achievements)
        
    except Exception as e:
        return jsonify({"error": "Failed to fetch achievements", "details": str(e)}), 500
    finally:
        cur.close()
        conn.close()

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