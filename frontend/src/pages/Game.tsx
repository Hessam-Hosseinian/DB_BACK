import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../store/gameStore';
import { useAuthStore } from '../store/authStore';
import FindingOpponent from '../components/game/FindingOpponent';
import CategorySelection from '../components/game/CategorySelection';
import QuizQuestion from '../components/game/QuizQuestion';
import RoundResults from '../components/game/RoundResults';
import GameOver from '../components/game/GameOver';

const Game = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { status, findOpponent } = useGameStore();

  useEffect(() => {
    // Auto-start matchmaking when entering the game page
    if (status === 'idle') {
      findOpponent();
    }
  }, [status, findOpponent]);

  const renderGameContent = () => {
    switch (status) {
      case 'finding-opponent':
        return <FindingOpponent />;
      case 'category-selection':
        return <CategorySelection />;
      case 'playing':
        return <QuizQuestion />;
      case 'round-results':
        return <RoundResults />;
      case 'game-over':
        return <GameOver />;
      default:
        return <FindingOpponent />;
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="flex-grow max-w-4xl mx-auto w-full px-4"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={status}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="w-full"
          >
            {renderGameContent()}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Game;