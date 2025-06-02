import pytest
from datetime import datetime
from flask import session
from models.game_model import Game
from models.user_model import User
from models.matchmaking import Matchmaker

def test_create_game_with_opponent(client, test_user):
    """Test creating a new game with a specific opponent"""
    # Create test users and login
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create opponent
    opponent = User(
        username="opponent",
        email="opponent@example.com",
        password="hashed_password"
    )
    opponent.id = 2
    
    data = {
        'opponent_id': 2,
        'game_type': 'standard',
        'config': {'rounds': 5}
    }
    
    response = client.post('/api/games/new', json=data)
    assert response.status_code == 201
    
    json_data = response.get_json()
    assert 'game_id' in json_data
    assert json_data['status'] == 'pending'
    assert json_data['opponent_id'] == 2

def test_create_game_with_matchmaking(client, test_user, monkeypatch):
    """Test creating a new game using matchmaking"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Mock matchmaker to return a fixed opponent
    def mock_find_match(user_id):
        return 2
    monkeypatch.setattr(Matchmaker, 'find_match', mock_find_match)
    
    data = {
        'game_type': 'standard',
        'config': {'rounds': 5}
    }
    
    response = client.post('/api/games/new', json=data)
    assert response.status_code == 201
    
    json_data = response.get_json()
    assert 'game_id' in json_data
    assert json_data['opponent_id'] == 2

def test_get_game_details(client, test_user):
    """Test getting game details"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create a test game
    game = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard'
    )
    game.id = 1
    game.save()
    
    response = client.get('/api/games/1')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['game_type'] == 'standard'
    assert json_data['player1_id'] == 1
    assert json_data['player2_id'] == 2

def test_unauthorized_game_access(client, test_user):
    """Test unauthorized access to game details"""
    with client.session_transaction() as sess:
        sess['user_id'] = 3  # User not in the game
    
    # Create a test game
    game = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard'
    )
    game.id = 1
    game.save()
    
    response = client.get('/api/games/1')
    assert response.status_code == 403

def test_make_move(client, test_user):
    """Test making a move in the game"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create an active game
    game = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard',
        status='active'
    )
    game.id = 1
    game.save()
    
    move_data = {
        'round_number': 1,
        'points': 10,
        'answer_time': 2.5
    }
    
    response = client.post('/api/games/1/move', json=move_data)
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert 'current_scores' in json_data

def test_finish_game(client, test_user):
    """Test finishing a game"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create an active game
    game = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard',
        status='active'
    )
    game.id = 1
    game.player1_score = 50
    game.player2_score = 30
    game.save()
    
    move_data = {
        'round_number': 5,
        'points': 10,
        'is_final_round': True
    }
    
    response = client.post('/api/games/1/move', json=move_data)
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['status'] == 'finished'
    assert json_data['winner_id'] == 1
    assert json_data['final_scores']['player1'] == 60

def test_get_active_games(client, test_user):
    """Test getting active games list"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create some test games
    game1 = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard',
        status='active'
    )
    game1.id = 1
    game1.save()
    
    game2 = Game(
        player1_id=1,
        player2_id=3,
        game_type='standard',
        status='pending'
    )
    game2.id = 2
    game2.save()
    
    response = client.get('/api/games/active')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert len(json_data['games']) == 2
    assert any(g['status'] == 'active' for g in json_data['games'])
    assert any(g['status'] == 'pending' for g in json_data['games'])

def test_forfeit_game(client, test_user):
    """Test forfeiting a game"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create an active game
    game = Game(
        player1_id=1,
        player2_id=2,
        game_type='standard',
        status='active'
    )
    game.id = 1
    game.save()
    
    response = client.post('/api/games/1/forfeit')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['status'] == 'finished'
    assert json_data['winner_id'] == 2
    assert 'Game forfeited' in json_data['message']

def test_game_history(client, test_user):
    """Test getting game history"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create some finished games
    for i in range(3):
        game = Game(
            player1_id=1,
            player2_id=2,
            game_type='standard',
            status='finished',
            winner_id=1 if i % 2 == 0 else 2
        )
        game.id = i + 1
        game.end_time = datetime.now()
        game.save()
    
    response = client.get('/api/games/history')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert len(json_data['games']) == 3
    assert json_data['pagination']['total'] == 3
    assert all(g['winner_id'] in [1, 2] for g in json_data['games'])

def test_player_stats(client, test_user):
    """Test getting player statistics"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    # Create some finished games with different outcomes
    for i in range(5):
        game = Game(
            player1_id=1,
            player2_id=2,
            game_type='standard',
            status='finished',
            winner_id=1 if i < 3 else 2  # Player wins 3 out of 5 games
        )
        game.id = i + 1
        game.player1_score = 100 if i < 3 else 80
        game.end_time = datetime.now()
        game.save()
    
    response = client.get('/api/games/stats')
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['total_games'] == 5
    assert json_data['wins'] == 3
    assert json_data['losses'] == 2
    assert json_data['win_rate'] == 60.0
    assert 80 <= json_data['avg_score'] <= 100
    assert json_data['highest_score'] == 100

def test_unauthenticated_access(client):
    """Test accessing endpoints without authentication"""
    endpoints = [
        ('POST', '/api/games/new'),
        ('GET', '/api/games/1'),
        ('POST', '/api/games/1/move'),
        ('GET', '/api/games/active'),
        ('POST', '/api/games/1/forfeit'),
        ('GET', '/api/games/history'),
        ('GET', '/api/games/stats')
    ]
    
    for method, endpoint in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'Authentication required' in json_data['error']

def test_invalid_game_id(client, test_user):
    """Test accessing non-existent game"""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    
    endpoints = [
        ('GET', '/api/games/999'),
        ('POST', '/api/games/999/move'),
        ('POST', '/api/games/999/forfeit')
    ]
    
    for method, endpoint in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)
        
        assert response.status_code == 404
        json_data = response.get_json()
        assert 'Game not found' in json_data['error'] 