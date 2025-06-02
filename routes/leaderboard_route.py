from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.leaderboard_model import Leaderboard
from db.database import db_session
from sqlalchemy import text

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/api/leaderboard/top', methods=['GET'])
def get_top_players():
    """Get top players on the leaderboard"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        players = Leaderboard.get_top_players(db_session, limit)
        
        return jsonify({
            'status': 'success',
            'data': [{
                'username': player.user.username,
                'score': player.score,
                'games_played': player.games_played,
                'win_streak': player.win_streak,
                'highest_score': player.highest_score,
                'average_score': float(player.average_score)
            } for player in players]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/player/<int:user_id>', methods=['GET'])
def get_player_stats(user_id):
    """Get detailed stats for a specific player"""
    try:
        # Get player's rank information
        rank_info = Leaderboard.get_player_rank(db_session, user_id)
        if not rank_info:
            return jsonify({'status': 'error', 'message': 'Player not found'}), 404

        # Get nearby players
        nearby_range = min(int(request.args.get('range', 2)), 5)
        nearby_players = Leaderboard.get_nearby_players(db_session, user_id, nearby_range)

        # Get player's leaderboard entry
        player = db_session.query(Leaderboard).filter_by(user_id=user_id).first()
        
        return jsonify({
            'status': 'success',
            'data': {
                'player': {
                    'username': player.user.username,
                    'score': player.score,
                    'games_played': player.games_played,
                    'win_streak': player.win_streak,
                    'highest_score': player.highest_score,
                    'average_score': float(player.average_score),
                    'rank': rank_info.rank,
                    'percentile': float(rank_info.percentile)
                },
                'nearby_players': [{
                    'username': p.username,
                    'score': p.score,
                    'position': p.position
                } for p in nearby_players]
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/update', methods=['POST'])
@login_required
def update_player_score():
    """Update player's score"""
    try:
        data = request.get_json()
        if 'score' not in data:
            return jsonify({'status': 'error', 'message': 'Score is required'}), 400

        player = db_session.query(Leaderboard).filter_by(user_id=current_user.id).first()
        if not player:
            player = Leaderboard(user_id=current_user.id)
            db_session.add(player)
            db_session.commit()

        player.update_score(db_session, data['score'])
        
        return jsonify({'status': 'success', 'message': 'Score updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/stats', methods=['GET'])
def get_leaderboard_stats():
    """Get general leaderboard statistics"""
    try:
        stats = db_session.execute(text("""
            SELECT 
                COUNT(*) as total_players,
                MAX(score) as highest_score,
                AVG(score)::numeric(10,2) as average_score,
                MAX(games_played) as most_games_played,
                MAX(win_streak) as highest_streak
            FROM leaderboard
        """)).first()

        return jsonify({
            'status': 'success',
            'data': {
                'total_players': stats.total_players,
                'highest_score': stats.highest_score,
                'average_score': float(stats.average_score),
                'most_games_played': stats.most_games_played,
                'highest_streak': stats.highest_streak
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
