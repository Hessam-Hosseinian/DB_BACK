import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Trophy, Home, User, LogOut, Menu, X } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Home', path: '/', icon: <Home size={20} /> },
    { name: 'Leaderboard', path: '/leaderboard', icon: <Trophy size={20} /> },
    { name: 'Profile', path: '/profile', icon: <User size={20} /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-secondary-800 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 10 }}
              whileTap={{ scale: 0.9 }}
              className="text-primary-600"
            >
              <Brain size={28} />
            </motion.div>
            <span className="font-display text-lg font-bold">Quiz Challenge</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 rounded-lg transition-colors duration-200 ${
                  isActive(item.path)
                    ? 'bg-primary-700 text-white'
                    : 'text-secondary-300 hover:bg-secondary-700 hover:text-white'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
              </Link>
            ))}

            <button
              onClick={handleLogout}
              className="flex items-center px-3 py-2 rounded-lg text-secondary-300 hover:bg-secondary-700 hover:text-white transition-colors duration-200"
            >
              <LogOut size={20} className="mr-2" />
              Logout
            </button>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-secondary-300 hover:bg-secondary-700 hover:text-white transition-colors duration-200"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden bg-secondary-800 border-t border-secondary-700"
          >
            <div className="container mx-auto px-4 py-3 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-3 rounded-lg transition-colors duration-200 ${
                    isActive(item.path)
                      ? 'bg-primary-700 text-white'
                      : 'text-secondary-300 hover:bg-secondary-700 hover:text-white'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <span className="mr-3">{item.icon}</span>
                  {item.name}
                </Link>
              ))}

              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="w-full flex items-center px-3 py-3 rounded-lg text-secondary-300 hover:bg-secondary-700 hover:text-white transition-colors duration-200"
              >
                <LogOut size={20} className="mr-3" />
                Logout
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;