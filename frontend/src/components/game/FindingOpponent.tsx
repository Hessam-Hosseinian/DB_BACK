import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, X } from 'lucide-react';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

const FindingOpponent = () => {
  const { user } = useAuthStore();
  const { cancelMatchmaking } = useGameStore();
  const navigate = useNavigate();
  const [searchTime, setSearchTime] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSearchTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const handleCancel = () => {
    cancelMatchmaking();
    navigate('/');
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex items-center justify-center">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="bg-secondary-800 rounded-xl p-8 w-full max-w-md text-center shadow-xl"
      >
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 0, 0, 0, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            repeatType: "reverse"
          }}
          className="bg-primary-700/20 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6"
        >
          <Search size={32} className="text-primary-500" />
        </motion.div>

        <h2 className="text-2xl font-display font-bold mb-2">Finding Opponent</h2>
        <p className="text-secondary-400 mb-8">Looking for a worthy challenger...</p>

        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-secondary-700 border-2 border-primary-600 overflow-hidden">
                <img 
                  src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'Player'}`}
                  alt="Your Avatar"
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="mt-2 font-medium">{user?.username || 'You'}</span>
            </div>

            <motion.div
              animate={{ 
                x: [0, 10, 0, -10, 0],
                rotate: [0, 5, 0, -5, 0]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                repeatType: "loop"
              }}
              className="text-primary-500 font-bold text-xl"
            >
              VS
            </motion.div>

            <div className="flex flex-col items-center">
              <motion.div 
                animate={{ 
                  opacity: [0.5, 1, 0.5],
                  scale: [0.95, 1, 0.95]
                }}
                transition={{ 
                  duration: 1.5,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
                className="w-16 h-16 rounded-full bg-secondary-700 border-2 border-secondary-600 flex items-center justify-center"
              >
                <span className="text-secondary-400 text-2xl">?</span>
              </motion.div>
              <span className="mt-2 font-medium text-secondary-400">Searching...</span>
            </div>
          </div>
        </div>

        <div className="w-full bg-secondary-700 h-2 rounded-full overflow-hidden mb-6">
          <motion.div 
            animate={{ 
              width: ["0%", "100%", "0%"]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="h-full bg-primary-600"
          />
        </div>

        <p className="text-secondary-400 mb-6">Search time: {formatTime(searchTime)}</p>

        <button 
          onClick={handleCancel}
          className="btn-outline flex items-center justify-center mx-auto"
        >
          <X size={16} className="mr-2" />
          Cancel Search
        </button>
      </motion.div>
    </div>
  );
};

export default FindingOpponent;