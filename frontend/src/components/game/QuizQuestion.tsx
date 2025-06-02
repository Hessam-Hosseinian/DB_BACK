import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';
import { Clock } from 'lucide-react';

const QuizQuestion = () => {
  const { user } = useAuthStore();
  const { 
    questions, 
    currentQuestionIndex, 
    selectedAnswer, 
    selectAnswer,
    currentRound,
    selectedCategory,
    opponent,
    timer: initialTimer,
    playerScore,
    opponentScore
  } = useGameStore();
  
  const [timer, setTimer] = useState(initialTimer);
  const currentQuestion = questions[currentQuestionIndex];
  
  useEffect(() => {
    if (selectedAnswer !== null) return;
    
    const countdown = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          clearInterval(countdown);
          // Auto-select an answer when time runs out
          selectAnswer(Math.floor(Math.random() * 4));
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(countdown);
  }, [selectedAnswer, selectAnswer]);
  
  // Reset timer when moving to a new question
  useEffect(() => {
    setTimer(initialTimer);
  }, [currentQuestionIndex, initialTimer]);
  
  const getOptionClassName = (index: number) => {
    if (selectedAnswer === null) {
      return "quiz-option";
    }
    
    if (index === currentQuestion.correctAnswer) {
      return "quiz-option correct";
    }
    
    if (index === selectedAnswer && index !== currentQuestion.correctAnswer) {
      return "quiz-option incorrect";
    }
    
    return "quiz-option";
  };

  return (
    <div className="py-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-secondary-700 border-2 border-primary-600 overflow-hidden">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'Player'}`}
                alt="Your Avatar"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h3 className="font-medium">{user?.username || 'You'}</h3>
              <p className="text-primary-500 font-semibold">{playerScore} pts</p>
            </div>
          </div>

          <div className="flex flex-col items-center">
            <div className="px-4 py-2 bg-secondary-800 rounded-lg mb-2">
              <span className="text-secondary-400 mr-2">Round:</span>
              <span className="font-bold">{currentRound}/5</span>
            </div>
            <div className="px-4 py-1 bg-primary-700/20 rounded-lg">
              <span className="text-primary-500 font-medium text-sm">{selectedCategory?.name}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div>
              <h3 className="font-medium text-right">{opponent?.username || 'Opponent'}</h3>
              <p className="text-secondary-400 font-semibold text-right">{opponentScore} pts</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-secondary-700 border-2 border-secondary-600 overflow-hidden">
              <img 
                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${opponent?.username || 'Opponent'}`}
                alt="Opponent Avatar"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>
      </motion.div>

      <div className="mb-2 flex justify-between items-center">
        <span className="text-secondary-400">Question {currentQuestionIndex + 1} of {questions.length}</span>
        <div className="flex items-center bg-secondary-800 px-3 py-1 rounded-lg">
          <Clock size={16} className="mr-1 text-secondary-400" />
          <motion.span
            key={timer}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
            className={`font-medium ${timer <= 5 ? 'text-error' : 'text-secondary-300'}`}
          >
            {timer}s
          </motion.span>
        </div>
      </div>

      <div className="w-full bg-secondary-800 h-2 rounded-full mb-8">
        <motion.div 
          initial={{ width: '100%' }}
          animate={{ width: `${(timer / initialTimer) * 100}%` }}
          transition={{ duration: 0.5 }}
          className={`h-full rounded-full ${timer <= 5 ? 'bg-error' : 'bg-primary-600'}`}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="bg-secondary-800 rounded-xl p-6 mb-6"
          >
            <h3 className="text-xl md:text-2xl font-medium mb-2">{currentQuestion.question}</h3>
          </motion.div>

          <div className="space-y-4">
            {currentQuestion.options.map((option, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={selectedAnswer === null ? { scale: 1.02 } : {}}
                whileTap={selectedAnswer === null ? { scale: 0.98 } : {}}
                onClick={() => selectedAnswer === null && selectAnswer(index)}
                className={getOptionClassName(index)}
              >
                <div className="w-8 h-8 rounded-full bg-secondary-700 flex items-center justify-center mr-2">
                  {String.fromCharCode(65 + index)}
                </div>
                {option}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default QuizQuestion;