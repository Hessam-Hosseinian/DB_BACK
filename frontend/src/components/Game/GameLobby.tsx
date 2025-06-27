import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import { Sword, Users, Search, Clock, ArrowLeft } from 'lucide-react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import LoadingSpinner from '../UI/LoadingSpinner';
import { gameAPI } from '../../services/api';

const GameLobby: React.FC = () => {
  const { user } = useAuth();
  const { gameMode, setGameMode } = useGame();
  const navigate = useNavigate();
  const [isSearching, setIsSearching] = useState(false);
  const [searchTime, setSearchTime] = useState(0);

  useEffect(() => {
    if (!gameMode) {
      navigate('/dashboard');
      return;
    }

    let interval: NodeJS.Timeout;
    if (isSearching) {
      interval = setInterval(() => {
        setSearchTime(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [gameMode, navigate, isSearching]);

  const handleFindMatch = async () => {
    if (!user) return;

    setIsSearching(true);
    setSearchTime(0);

    try {
      const gameTypeId = gameMode === 'duel' ? 1 : 2;
      const result = await gameAPI.joinQueue(user.id, gameTypeId);
      
      if (result.game_id) {
        // Match found immediately
        navigate(`/game/${result.game_id}`);
      } else {
        // Added to queue, simulate finding a match after a delay
        setTimeout(() => {
          setIsSearching(false);
          navigate(`/game/123`); // Mock game ID
        }, 3000 + Math.random() * 5000);
      }
    } catch (error) {
      console.error('Failed to find match:', error);
      setIsSearching(false);
    }
  };

  const handleCancelSearch = () => {
    setIsSearching(false);
    setSearchTime(0);
  };

  const handleBack = () => {
    setGameMode(null);
    navigate('/dashboard');
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!gameMode) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="flex items-center space-x-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleBack}
          className="text-gray-400 hover:text-white"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-3xl font-bold text-white">
          {gameMode === 'duel' ? 'Duel Lobby' : 'Multiplayer Lobby'}
        </h1>
      </div>

      <Card className="text-center">
        <div className="p-8">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
            {gameMode === 'duel' ? (
              <Sword className="h-12 w-12 text-white" />
            ) : (
              <Users className="h-12 w-12 text-white" />
            )}
          </div>

          <h2 className="text-2xl font-bold text-white mb-4">
            {gameMode === 'duel' ? 'Duel Mode' : 'Multiplayer Mode'}
          </h2>

          <p className="text-gray-300 mb-8 max-w-md mx-auto">
            {gameMode === 'duel' 
              ? 'Face off against another player in a 5-round quiz battle. Each round, one player picks the category!'
              : 'Join up to 8 players in a group quiz with 10 questions across various categories.'
            }
          </p>

          {!isSearching ? (
            <div className="space-y-4">
              <Button
                variant="primary"
                size="lg"
                onClick={handleFindMatch}
                className="w-full max-w-xs mx-auto"
              >
                <Search className="h-5 w-5 mr-2" />
                Find Match
              </Button>
              
              <div className="text-sm text-gray-400">
                <p>We'll match you with players of similar skill level</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center justify-center space-x-3">
                <LoadingSpinner size="medium" />
                <span className="text-white text-lg">Searching for opponents...</span>
              </div>

              <div className="flex items-center justify-center space-x-2 text-orange-400">
                <Clock className="h-4 w-4" />
                <span className="font-mono text-lg">{formatTime(searchTime)}</span>
              </div>

              <Button
                variant="secondary"
                onClick={handleCancelSearch}
                className="w-full max-w-xs mx-auto"
              >
                Cancel Search
              </Button>

              <div className="text-sm text-gray-400">
                <p>Average wait time: 30-60 seconds</p>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Game Rules */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-white mb-4">How to Play</h3>
          <div className="space-y-3 text-gray-300">
            {gameMode === 'duel' ? (
              <>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">1</span>
                  <p>Each game consists of 5 rounds</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">2</span>
                  <p>At the start of each round, one player chooses a category</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">3</span>
                  <p>Both players answer the same question from that category</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">4</span>
                  <p>Points are awarded based on correctness and speed</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">5</span>
                  <p>Player with the most points after 5 rounds wins!</p>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">1</span>
                  <p>All players answer the same 10 questions</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">2</span>
                  <p>Questions are from various categories</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">3</span>
                  <p>Each question has a 30-second time limit</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">4</span>
                  <p>Points are awarded for correct answers and speed</p>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">5</span>
                  <p>Player with the highest score wins!</p>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default GameLobby;