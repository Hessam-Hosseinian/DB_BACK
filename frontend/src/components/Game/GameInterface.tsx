import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import { Clock, Trophy, Users, CheckCircle, XCircle } from 'lucide-react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import LoadingSpinner from '../UI/LoadingSpinner';

interface Question {
  id: number;
  text: string;
  choices: Array<{
    id: number;
    text: string;
    is_correct: boolean;
  }>;
}

interface GameState {
  id: number;
  status: 'pending' | 'active' | 'completed';
  current_round: number;
  total_rounds: number;
  participants: Array<{
    id: number;
    username: string;
    score: number;
  }>;
  current_question?: Question;
  time_remaining: number;
  category?: string;
  show_category_selection?: boolean;
  categories?: Array<{ id: number; name: string; description: string }>;
}

const GameInterface: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const { user } = useAuth();
  const { gameMode } = useGame();
  const navigate = useNavigate();
  
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [hasAnswered, setHasAnswered] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [loading, setLoading] = useState(true);

  // Mock game state - in real app, this would come from WebSocket or API
  useEffect(() => {
    const mockGame: GameState = {
      id: parseInt(gameId || '0'),
      status: 'active',
      current_round: 1,
      total_rounds: gameMode === 'duel' ? 5 : 1,
      participants: [
        { id: user?.id || 1, username: user?.username || 'You', score: 0 },
        { id: 2, username: 'Opponent', score: 0 },
      ],
      current_question: {
        id: 1,
        text: "What is the capital of France?",
        choices: [
          { id: 1, text: "Paris", is_correct: true },
          { id: 2, text: "London", is_correct: false },
          { id: 3, text: "Berlin", is_correct: false },
          { id: 4, text: "Madrid", is_correct: false },
        ]
      },
      time_remaining: 30,
      category: "Geography",
      show_category_selection: false,
    };

    setGameState(mockGame);
    setLoading(false);

    // Simulate timer
    const timer = setInterval(() => {
      setGameState(prev => {
        if (!prev || prev.time_remaining <= 0) return prev;
        return { ...prev, time_remaining: prev.time_remaining - 1 };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [gameId, gameMode, user]);

  const handleAnswerSelect = (choiceId: number) => {
    if (hasAnswered || !gameState?.current_question) return;
    
    setSelectedAnswer(choiceId);
    setHasAnswered(true);
    
    const correct = gameState.current_question.choices.find(c => c.id === choiceId)?.is_correct || false;
    setIsCorrect(correct);
    setShowResult(true);

    // Simulate showing result for 2 seconds then next question
    setTimeout(() => {
      setShowResult(false);
      setHasAnswered(false);
      setSelectedAnswer(null);
      // In real app, this would trigger next question via WebSocket
    }, 2000);
  };

  const handleGameComplete = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-4">Game not found</h2>
        <Button onClick={() => navigate('/dashboard')}>Return to Dashboard</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Game Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">
            {gameMode === 'duel' ? 'Duel Battle' : 'Multiplayer Quiz'}
          </h1>
          <p className="text-gray-300">
            Round {gameState.current_round} of {gameState.total_rounds} • {gameState.category}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-orange-500/20 px-4 py-2 rounded-lg border border-orange-500/30">
            <Clock className="h-4 w-4 text-orange-400" />
            <span className="text-orange-400 font-mono font-bold text-lg">
              {gameState.time_remaining}s
            </span>
          </div>
        </div>
      </div>

      {/* Players */}
      <div className="grid grid-cols-2 gap-4">
        {gameState.participants.map((participant) => (
          <Card key={participant.id} className={participant.id === user?.id ? 'border-orange-500/30' : ''}>
            <div className="p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-medium">{participant.username}</h3>
                  <p className="text-gray-400 text-sm">
                    {participant.id === user?.id ? 'You' : 'Opponent'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-orange-400">{participant.score}</div>
                <div className="text-gray-400 text-sm">points</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Question */}
      {gameState.current_question && (
        <Card>
          <div className="p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-white mb-4">
                {gameState.current_question.text}
              </h2>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-orange-500 to-orange-600 h-2 rounded-full transition-all duration-1000"
                  style={{ width: `${(gameState.time_remaining / 30) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {gameState.current_question.choices.map((choice, index) => {
                const isSelected = selectedAnswer === choice.id;
                const isCorrectChoice = choice.is_correct;
                
                let buttonClass = 'w-full p-4 text-left transition-all duration-200 ';
                
                if (showResult) {
                  if (isCorrectChoice) {
                    buttonClass += 'bg-green-500/20 border-green-500/50 text-green-400';
                  } else if (isSelected && !isCorrectChoice) {
                    buttonClass += 'bg-red-500/20 border-red-500/50 text-red-400';
                  } else {
                    buttonClass += 'bg-gray-500/20 border-gray-500/30 text-gray-400';
                  }
                } else if (isSelected) {
                  buttonClass += 'bg-orange-500/20 border-orange-500/50 text-orange-400';
                } else {
                  buttonClass += 'bg-gray-800/50 border-gray-600/30 text-white hover:bg-orange-500/10 hover:border-orange-500/30';
                }

                return (
                  <button
                    key={choice.id}
                    onClick={() => handleAnswerSelect(choice.id)}
                    disabled={hasAnswered}
                    className={`${buttonClass} border-2 rounded-lg flex items-center space-x-3`}
                  >
                    <div className="w-8 h-8 bg-current/20 rounded-full flex items-center justify-center text-sm font-bold">
                      {String.fromCharCode(65 + index)}
                    </div>
                    <span className="font-medium">{choice.text}</span>
                    {showResult && (
                      <div className="ml-auto">
                        {isCorrectChoice ? (
                          <CheckCircle className="h-5 w-5 text-green-400" />
                        ) : isSelected ? (
                          <XCircle className="h-5 w-5 text-red-400" />
                        ) : null}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {showResult && (
              <div className="mt-6 text-center">
                <div className={`text-lg font-bold ${isCorrect ? 'text-green-400' : 'text-red-400'}`}>
                  {isCorrect ? '🎉 Correct!' : '❌ Incorrect'}
                </div>
                <p className="text-gray-400 mt-2">
                  {isCorrect ? 'Great job! You earned points.' : 'Better luck next time!'}
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Game Complete */}
      {gameState.status === 'completed' && (
        <Card>
          <div className="p-8 text-center">
            <Trophy className="h-16 w-16 text-orange-400 mx-auto mb-4" />
            <h2 className="text-3xl font-bold text-white mb-4">Game Complete!</h2>
            <p className="text-gray-300 mb-6">
              Winner: {gameState.participants.reduce((a, b) => a.score > b.score ? a : b).username}
            </p>
            <Button variant="primary" onClick={handleGameComplete}>
              Return to Dashboard
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default GameInterface;