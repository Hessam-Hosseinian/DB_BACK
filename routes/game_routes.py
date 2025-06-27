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
        game_type_id = data.get('game_type_id')
        if not game_type_id:
            return jsonify({'error': 'Game type is required'}), 400
            
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

        # Create new game with participants
        game = Game(game_type_id=game_type_id, game_config=game_config)
        game.create([session['user_id'], opponent_id])
        
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
            
        # Check if user is a participant
        participant_ids = [p['user_id'] for p in game.participants]
        if session['user_id'] not in participant_ids:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        game_data = {
            'id': game.id,
            'status': game.status,
            'game_type_id': game.game_type_id,
            'config': game.game_config,
            'start_time': game.start_time.isoformat() if game.start_time else None,
            'end_time': game.end_time.isoformat() if game.end_time else None,
            'participants': game.participants,
            'current_round': game.current_round
        }
            
        return jsonify(game_data), 200

    except GameError as e:
        return jsonify({'error': str(e)}), 500

@game_bp.route('/<int:game_id>/answer', methods=['POST'])
@login_required
def submit_answer(game_id: int):
    """Submit an answer for the current round"""
    try:
        game = Game.find_by_id(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
            
        # Check if user is a participant
        participant_ids = [p['user_id'] for p in game.participants]
        if session['user_id'] not in participant_ids:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        if game.status != 'active':
            return jsonify({'error': 'Game is not active'}), 400

        if not game.current_round:
            return jsonify({'error': 'No active round found'}), 400

        data = request.get_json()
        choice_id = data.get('choice_id')
        if not choice_id:
            return jsonify({'error': 'Choice ID is required'}), 400
            
        response_time = data.get('response_time_ms', 0)
        
        # Submit answer and get result
        result = game.submit_answer(
            user_id=session['user_id'],
            round_id=game.current_round['id'],
            choice_id=choice_id,
            response_time_ms=response_time
        )
        
        # Get updated leaderboard
        leaderboard = game.get_leaderboard()
        
        response = {
            'result': result,
            'leaderboard': leaderboard
        }
        
        # Check if this was the final round
        if data.get('is_final_round', False):
            game.finish_game()
            response['game_finished'] = True
            
        return jsonify(response), 200

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
            SELECT g.id, g.status, gt.name as game_type, g.start_time,
                   json_agg(json_build_object(
                       'user_id', u.id,
                       'username', u.username,
                       'score', gp.score
                   )) as participants
            FROM games g
            JOIN game_types gt ON g.game_type_id = gt.id
            JOIN game_participants gp ON g.id = gp.game_id
            JOIN users u ON gp.user_id = u.id
            WHERE EXISTS (
                SELECT 1 FROM game_participants 
                WHERE game_id = g.id AND user_id = %s
            )
            AND g.status IN ('pending', 'active')
            GROUP BY g.id, gt.name
            ORDER BY g.start_time DESC
        """, (session['user_id'],))
        
        games = []
        for row in cur.fetchall():
            participants = row[4]
            opponent = next(
                (p for p in participants if p['user_id'] != session['user_id']),
                None
            )
            
            games.append({
                'game_id': row[0],
                'status': row[1],
                'game_type': row[2],
                'start_time': row[3].isoformat() if row[3] else None,
                'opponent': opponent,
                'your_score': next(
                    p['score'] for p in participants 
                    if p['user_id'] == session['user_id']
                )
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
            
        # Check if user is a participant
        participant_ids = [p['user_id'] for p in game.participants]
        if session['user_id'] not in participant_ids:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        if game.status != 'active':
            return jsonify({'error': 'Game is not active'}), 400
            
        # Update game status and participant status
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                WITH game_update AS (
                    UPDATE games 
                    SET status = 'finished',
                        end_time = NOW()
                    WHERE id = %s
                    RETURNING id
                )
                UPDATE game_participants
                SET status = 'forfeit'
                WHERE game_id = %s AND user_id = %s
            """, (game_id, game_id, session['user_id']))
            conn.commit()
            
            return jsonify({
                'status': 'finished',
                'message': 'Game forfeited'
            }), 200
        finally:
            cur.close()
            conn.close()

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
            SELECT COUNT(DISTINCT g.id)
            FROM games g
            JOIN game_participants gp ON g.id = gp.game_id
            WHERE gp.user_id = %s AND g.status = 'finished'
        """, (session['user_id'],))
        total = cur.fetchone()[0]
        
        # Get paginated results
        cur.execute("""
            SELECT g.id, gt.name as game_type, g.start_time, g.end_time,
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
            WHERE EXISTS (
                SELECT 1 FROM game_participants 
                WHERE game_id = g.id AND user_id = %s
            )
            AND g.status = 'finished'
            GROUP BY g.id, gt.name
            ORDER BY g.end_time DESC
            LIMIT %s OFFSET %s
        """, (session['user_id'], per_page, (page - 1) * per_page))
        
        games = []
        for row in cur.fetchall():
            participants = row[4]
            opponent = next(
                (p for p in participants if p['user_id'] != session['user_id']),
                None
            )
            your_result = next(
                p for p in participants if p['user_id'] == session['user_id']
            )
            
            games.append({
                'game_id': row[0],
                'game_type': row[1],
                'start_time': row[2].isoformat() if row[2] else None,
                'end_time': row[3].isoformat() if row[3] else None,
                'opponent': opponent,
                'your_score': your_result['score'],
                'your_status': your_result['status'],
                'duration': (row[3] - row[2]).total_seconds() if row[2] and row[3] else None
            })
            
        return jsonify({
            'games': games,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
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
