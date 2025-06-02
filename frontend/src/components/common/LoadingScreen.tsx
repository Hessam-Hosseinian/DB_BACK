import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

const LoadingScreen = () => {
  return (
    <div className="fixed inset-0 bg-secondary-900 flex flex-col items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center"
      >
        <motion.div
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 10, -10, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="text-primary-600 mb-4"
        >
          <Brain size={60} />
        </motion.div>
        
        <motion.h1 
          className="text-2xl font-display font-bold mb-8 text-white"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          Quiz Challenge
        </motion.h1>
        
        <motion.div 
          className="w-48 h-2 bg-secondary-800 rounded-full overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <motion.div 
            className="h-full bg-primary-600 rounded-full"
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ 
              duration: 1.5,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut"
            }}
          />
        </motion.div>
        
        <motion.p 
          className="mt-4 text-secondary-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          Loading your quiz experience...
        </motion.p>
      </motion.div>
    </div>
  );
};

export default LoadingScreen;