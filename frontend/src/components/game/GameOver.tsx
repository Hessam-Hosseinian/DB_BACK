import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';
import { Home, RefreshCw, Trophy, Medal, Award } from 'lucide-react';
import Confetti from '../common/Confetti';

const GameOver = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { 
    playerScore, 
    opponentScore, 
    opponent,
    resetGame,
  } = useGameStore();
  
  const isWinner = playerScore > opponentScore;
  const isTie = playerScore === opponentScore;
  
  const handlePlayAgain = () => {
    resetGame();
    navigate('/game');
  };
  
  const handleGoHome = () => {
    resetGame();
    navigate('/');
  };

  return (
    <div className="py-8">
      {isWinner && <Confetti />}
      
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 300, damping: 15 }}
          className="inline-block mb-4"
        >
          {isWinner ? (
            <Trophy size={80} className="text-primary-500" />
          ) : isTie ? (
            <Medal size={80} className="text-primary-500" />
          ) : (
            <Award size={80} className="text-secondary-400" />
          )}
        </motion.div>
        
        <h2 className="text-4xl font-display font-bold mb-2">
          {isWinner ? 'You Won!' : isTie ? "It's a Tie!" : 'You Lost'}
        </h2>
        <p className="text-secondary-400 mb-4">
          {isWinner 
            ? 'Congratulations! Your knowledge has prevailed!' 
            : isTie 
              ? 'A perfectly matched battle of wits!' 
              : 'Better luck next time!'}
        </p>
        
        <div className="inline-block bg-secondary-800 px-6 py-3 rounded-lg">
          <span className="text-secondary-400 mr-2">Final Score:</span>
          <span className="text-primary-500 font-bold text-xl">{playerScore}</span>
          <span className="text-secondary-400 mx-2">to</span>
          <span className="font-bold text-xl">{opponentScore}</span>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="bg-secondary-800 rounded-xl p-6 mb-10"
      >
        <h3 className="text-xl font-display font-semibold mb-4">Match Summary</h3>
        
        <div className="flex flex-col md:flex-row justify-between items-center bg-secondary-700 rounded-lg p-4 mb-6">
          <div className="flex items-center mb-4 md:mb-0">
            <div className="w-16 h-16 rounded-full bg-secondary-600 border-2 border-primary-600 overflow-hidden mr-4">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'Player'}`}
                alt="Your Avatar"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h4 className="font-medium text-lg">{user?.username || 'You'}</h4>
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.6, type: "spring" }}
                className="bg-primary-700/20 text-primary-500 px-2 py-1 rounded text-sm inline-block"
              >
                {isWinner ? 'Winner' : isTie ? 'Tied' : 'Better luck next time'}
              </motion.div>
            </div>
          </div>
          
          <div className="flex items-center justify-center mb-4 md:mb-0">
            <motion.span 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="text-4xl font-display font-bold text-primary-500"
            >
              {playerScore}
            </motion.span>
            <span className="text-2xl mx-4">:</span>
            <motion.span 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="text-4xl font-display font-bold"
            >
              {opponentScore}
            </motion.span>
          </div>
          
          <div className="flex items-center">
            <div>
              <h4 className="font-medium text-lg text-right">{opponent?.username || 'Opponent'}</h4>
              <motion.div
                initial={{ scale: 0.5, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.6, type: "spring" }}
                className="bg-secondary-700/50 text-secondary-400 px-2 py-1 rounded text-sm inline-block"
              >
                {!isWinner && !isTie ? 'Winner' : isTie ? 'Tied' : 'Lost'}
              </motion.div>
            </div>
            <div className="w-16 h-16 rounded-full bg-secondary-600 border-2 border-secondary-500 overflow-hidden ml-4">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${opponent?.username || 'Opponent'}`}
                alt="Opponent Avatar"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-secondary-700 rounded p-3 text-center">
            <p className="text-secondary-400 text-sm mb-1">Total Rounds</p>
            <p className="font-semibold">5</p>
          </div>
          
          <div className="bg-secondary-700 rounded p-3 text-center">
            <p className="text-secondary-400 text-sm mb-1">Correct Answers</p>
            <p className="font-semibold">{playerScore / 10} / 15</p>
          </div>
          
          <div className="bg-secondary-700 rounded p-3 text-center">
            <p className="text-secondary-400 text-sm mb-1">Accuracy</p>
            <p className="font-semibold">{Math.round((playerScore / 10) / 15 * 100)}%</p>
          </div>
          
          <div className="bg-secondary-700 rounded p-3 text-center">
            <p className="text-secondary-400 text-sm mb-1">XP Earned</p>
            <p className="font-semibold text-primary-500">+{playerScore * 2}</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="flex flex-col md:flex-row justify-center gap-4"
      >
        <button 
          onClick={handlePlayAgain}
          className="btn-primary flex items-center justify-center"
        >
          <RefreshCw size={18} className="mr-2" />
          Play Again
        </button>
        
        <button 
          onClick={handleGoHome}
          className="btn-outline flex items-center justify-center"
        >
          <Home size={18} className="mr-2" />
          Return Home
        </button>
      </motion.div>
    </div>
  );
};

export default GameOver;