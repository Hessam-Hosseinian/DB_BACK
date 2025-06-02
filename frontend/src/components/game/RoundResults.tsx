import { motion } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';
import { Check, X, ArrowRight } from 'lucide-react';

const RoundResults = () => {
  const { user } = useAuthStore();
  const { 
    currentRound, 
    questions, 
    roundResults, 
    playerScore, 
    opponentScore,
    opponent,
    selectedCategory,
    startNextRound
  } = useGameStore();
  
  // Calculate round score
  const playerRoundScore = roundResults.playerCorrect.filter(Boolean).length * 10;
  const opponentRoundScore = roundResults.opponentCorrect.filter(Boolean).length * 10;
  
  // Determine round winner
  const roundWinner = playerRoundScore > opponentRoundScore 
    ? 'player' 
    : playerRoundScore < opponentRoundScore 
      ? 'opponent' 
      : 'tie';

  return (
    <div className="py-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <h2 className="text-3xl font-display font-bold mb-2">Round {currentRound} Results</h2>
        <p className="text-secondary-400 mb-2">Category: {selectedCategory?.name}</p>
        
        {roundWinner === 'player' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.5 }}
            className="bg-primary-700/20 text-primary-500 px-4 py-2 rounded-lg inline-block font-medium"
          >
            You won this round!
          </motion.div>
        )}
        
        {roundWinner === 'opponent' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.5 }}
            className="bg-secondary-700 text-secondary-300 px-4 py-2 rounded-lg inline-block font-medium"
          >
            Opponent won this round
          </motion.div>
        )}
        
        {roundWinner === 'tie' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.5 }}
            className="bg-secondary-700 text-secondary-300 px-4 py-2 rounded-lg inline-block font-medium"
          >
            It's a tie!
          </motion.div>
        )}
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-secondary-800 rounded-xl p-6"
        >
          <div className="flex items-center mb-6">
            <div className="w-12 h-12 rounded-full bg-secondary-700 border-2 border-primary-600 overflow-hidden mr-4">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'Player'}`}
                alt="Your Avatar"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h3 className="font-medium">{user?.username || 'You'}</h3>
              <div className="flex items-center">
                <span className="text-secondary-400 mr-2">Score:</span>
                <motion.span 
                  initial={{ color: '#FFFFFF' }}
                  animate={{ color: '#FF5722' }}
                  transition={{ duration: 1, delay: 0.5 }}
                  className="font-bold"
                >
                  {playerScore}
                </motion.span>
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 1 }}
                  className="text-primary-500 font-medium ml-2"
                >
                  (+{playerRoundScore})
                </motion.span>
              </div>
            </div>
          </div>

          <h4 className="font-medium mb-3">Your Answers:</h4>
          <div className="space-y-3">
            {questions.map((question, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                className="flex items-center"
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                  roundResults.playerCorrect[index] ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
                }`}>
                  {roundResults.playerCorrect[index] ? <Check size={14} /> : <X size={14} />}
                </div>
                <p className="text-sm text-secondary-300 truncate">{question.question}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-secondary-800 rounded-xl p-6"
        >
          <div className="flex items-center mb-6">
            <div className="w-12 h-12 rounded-full bg-secondary-700 border-2 border-secondary-600 overflow-hidden mr-4">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${opponent?.username || 'Opponent'}`}
                alt="Opponent Avatar"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h3 className="font-medium">{opponent?.username || 'Opponent'}</h3>
              <div className="flex items-center">
                <span className="text-secondary-400 mr-2">Score:</span>
                <span className="font-bold">{opponentScore}</span>
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 1 }}
                  className="text-secondary-400 font-medium ml-2"
                >
                  (+{opponentRoundScore})
                </motion.span>
              </div>
            </div>
          </div>

          <h4 className="font-medium mb-3">Opponent's Answers:</h4>
          <div className="space-y-3">
            {questions.map((question, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                className="flex items-center"
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                  roundResults.opponentCorrect[index] ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
                }`}>
                  {roundResults.opponentCorrect[index] ? <Check size={14} /> : <X size={14} />}
                </div>
                <p className="text-sm text-secondary-300 truncate">{question.question}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1 }}
        className="flex justify-center"
      >
        <button 
          onClick={startNextRound}
          className="btn-primary px-6 flex items-center"
        >
          {currentRound < 5 ? (
            <>
              Next Round
              <ArrowRight size={18} className="ml-2" />
            </>
          ) : (
            'See Final Results'
          )}
        </button>
      </motion.div>
    </div>
  );
};

export default RoundResults;