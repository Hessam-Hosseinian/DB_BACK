import { motion } from 'framer-motion';
import { useGameStore } from '../../store/gameStore';
import { useAuthStore } from '../../store/authStore';

const CategorySelection = () => {
  const { user } = useAuthStore();
  const { availableCategories, selectCategory, currentRound, opponent } = useGameStore();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: 'spring', stiffness: 300, damping: 24 }
    },
    hover: {
      scale: 1.05,
      boxShadow: "0 10px 25px -5px rgba(255, 87, 34, 0.4)",
      border: "2px solid #FF5722",
      transition: { type: 'spring', stiffness: 300, damping: 10 }
    },
    tap: {
      scale: 0.95
    }
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
              <p className="text-primary-500 text-sm font-semibold">Your turn to choose</p>
            </div>
          </div>

          <div className="px-4 py-2 bg-secondary-800 rounded-lg">
            <span className="text-secondary-400 mr-2">Round:</span>
            <span className="font-bold">{currentRound}/5</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div>
              <h3 className="font-medium text-right">{opponent?.username || 'Opponent'}</h3>
              <p className="text-secondary-400 text-sm text-right">Waiting for your choice</p>
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

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="text-center mb-10"
      >
        <h2 className="text-3xl font-display font-bold mb-2">Choose a Category</h2>
        <p className="text-secondary-400">Select one of the following categories for this round</p>
      </motion.div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {availableCategories.map((category) => (
          <motion.div
            key={category.id}
            variants={itemVariants}
            whileHover="hover"
            whileTap="tap"
            onClick={() => selectCategory(category.id)}
            className="bg-secondary-800 border-2 border-secondary-700 rounded-xl p-6 cursor-pointer"
          >
            <div className="text-4xl mb-4">{category.icon}</div>
            <h3 className="text-xl font-display font-semibold mb-2">{category.name}</h3>
            <p className="text-secondary-400">{category.description}</p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default CategorySelection;