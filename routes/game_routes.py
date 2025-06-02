from flask import Blueprint, jsonify, request, session
from functools import wraps
from typing import Dict, Any, Callable
from datetime import datetime

from models.game_model import Game
from models.user_model import User
from models.matchmaking import Matchmaker
from utils.exceptions import GameError, ValidationError
from db.connection import get_connection

game_bp = Blueprint('game', __name__, url_prefix='/games')

def login_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@game_bp.route('/new', methods=['POST'])
@login_required
def create_game():
    """Create a new game"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'standard')
        game_config = data.get('config', {})
        
        # Get opponent - either specified or via matchmaking
        opponent_id = data.get('opponent_id')
        if opponent_id:
            opponent = User.find_by_id(opponent_id)
            if not opponent:
                return jsonify({'error': 'Opponent not found'}), 404
        else:
            # Use matchmaking to find opponent
            matchmaker = Matchmaker()
            opponent_id = matchmaker.find_match(session['user_id'])
            if not opponent_id:
                return jsonify({'error': 'No matching opponent found'}), 404

        game = Game(
            player1_id=session['user_id'],
            player2_id=opponent_id,
            game_type=game_type,
            game_config=game_config
        )
        game.save()
        
        return jsonify({
            'game_id': game.id,
            'status': game.status,
            'opponent_id': opponent_id
        }), 201

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except GameError as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/<int:game_id>', methods=['GET'])
@login_required
def get_game(game_id: int):
    """Get game details"""
    try:
        game = Game.find_by_id(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
            
        if game.player1_id != session['user_id'] and game.player2_id != session['user_id']:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        return jsonify(game.get_stats()), 200

    except GameError as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/<int:game_id>/move', methods=['POST'])
@login_required
def make_move(game_id: int):
    """Submit a move/answer in the game"""
    try:
        game = Game.find_by_id(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
            
        if game.player1_id != session['user_id'] and game.player2_id != session['user_id']:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        if game.status != 'active':
            return jsonify({'error': 'Game is not active'}), 400

        data = request.get_json()
        round_results = {
            'round_number': data['round_number'],
            'player1_points': data.get('points', 0),
            'player2_points': 0,  # Will be updated when opponent moves
            'answer_times': {
                str(session['user_id']): data.get('answer_time')
            }
        }
        
        game.update_scores(round_results)
        
        # Check if game should be finished
        if data.get('is_final_round', False):
            winner_id = game.finish_game()
            return jsonify({
                'status': 'finished',
                'winner_id': winner_id,
                'final_scores': {
                    'player1': game.player1_score,
                    'player2': game.player2_score
                }
            }), 200
            
        return jsonify({
            'status': 'success',
            'current_scores': {
                'player1': game.player1_score,
                'player2': game.player2_score
            }
        }), 200

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except GameError as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/active', methods=['GET'])
@login_required
def get_active_games():
    """Get user's active games"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, player1_id, player2_id, status, game_type, start_time
            FROM games
            WHERE (player1_id = %s OR player2_id = %s)
            AND status IN ('pending', 'active')
            ORDER BY start_time DESC
        """, (session['user_id'], session['user_id']))
        
        games = []
        for row in cur.fetchall():
            opponent_id = row[2] if row[1] == session['user_id'] else row[1]
            opponent = User.find_by_id(opponent_id)
            
            games.append({
                'game_id': row[0],
                'status': row[3],
                'game_type': row[4],
                'start_time': row[5].isoformat() if row[5] else None,
                'opponent': {
                    'id': opponent_id,
                    'username': opponent.username if opponent else 'Unknown'
                }
            })
            
        return jsonify({'games': games}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@game_bp.route('/<int:game_id>/forfeit', methods=['POST'])
@login_required
def forfeit_game(game_id: int):
    """Forfeit a game"""
    try:
        game = Game.find_by_id(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
            
        if game.player1_id != session['user_id'] and game.player2_id != session['user_id']:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        if game.status != 'active':
            return jsonify({'error': 'Game is not active'}), 400
            
        # Set the other player as winner
        game.winner_id = game.player2_id if session['user_id'] == game.player1_id else game.player1_id
        game.status = 'finished'
        game.end_time = datetime.now()
        game.save()
        
        return jsonify({
            'status': 'finished',
            'winner_id': game.winner_id,
            'message': 'Game forfeited'
        }), 200

    except GameError as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/history', methods=['GET'])
@login_required
def get_game_history():
    """Get user's game history with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Get total count
        cur.execute("""
            SELECT COUNT(*)
            FROM games
            WHERE (player1_id = %s OR player2_id = %s)
            AND status = 'finished'
        """, (session['user_id'], session['user_id']))
        total = cur.fetchone()[0]
        
        # Get paginated results
        cur.execute("""
            SELECT id, player1_id, player2_id, winner_id, game_type, 
                   start_time, end_time, player1_score, player2_score
            FROM games
            WHERE (player1_id = %s OR player2_id = %s)
            AND status = 'finished'
            ORDER BY end_time DESC
            LIMIT %s OFFSET %s
        """, (session['user_id'], session['user_id'], per_page, (page - 1) * per_page))
        
        games = []
        for row in cur.fetchall():
            opponent_id = row[2] if row[1] == session['user_id'] else row[1]
            opponent = User.find_by_id(opponent_id)
            
            games.append({
                'game_id': row[0],
                'winner_id': row[3],
                'game_type': row[4],
                'start_time': row[5].isoformat() if row[5] else None,
                'end_time': row[6].isoformat() if row[6] else None,
                'scores': {
                    'player1': row[7],
                    'player2': row[8]
                },
                'opponent': {
                    'id': opponent_id,
                    'username': opponent.username if opponent else 'Unknown'
                }
            })
        
        return jsonify({
            'games': games,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@game_bp.route('/stats', methods=['GET'])
@login_required
def get_player_stats():
    """Get player's game statistics"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_games,
                COUNT(*) FILTER (WHERE 
                    (player1_id = %s AND winner_id = player1_id) OR
                    (player2_id = %s AND winner_id = player2_id)
                ) as wins,
                AVG(CASE 
                    WHEN player1_id = %s THEN player1_score
                    ELSE player2_score
                END) as avg_score,
                MAX(CASE 
                    WHEN player1_id = %s THEN player1_score
                    ELSE player2_score
                END) as highest_score
            FROM games
            WHERE (player1_id = %s OR player2_id = %s)
            AND status = 'finished'
        """, (session['user_id'], session['user_id'], session['user_id'],
              session['user_id'], session['user_id'], session['user_id']))
        
        row = cur.fetchone()
        
        stats = {
            'total_games': row[0],
            'wins': row[1],
            'losses': row[0] - row[1],
            'win_rate': round(row[1] / row[0] * 100, 2) if row[0] > 0 else 0,
            'avg_score': round(row[2], 2) if row[2] else 0,
            'highest_score': row[3] if row[3] else 0
        }
        
        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
