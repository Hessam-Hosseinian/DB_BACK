import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { LogOut, Trophy, Zap } from 'lucide-react';
import Button from '../UI/Button';

const Header: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-black/50 backdrop-blur-sm border-b border-orange-500/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">QuizBattle</h1>
              <p className="text-sm text-gray-400">Challenge Your Mind</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-gradient-to-r from-orange-500/10 to-orange-600/10 rounded-lg px-4 py-2 border border-orange-500/20">
              <Trophy className="h-4 w-4 text-orange-400" />
              <span className="text-white font-medium">{user?.username}</span>
              <span className="text-orange-400 text-sm">Lv.{user?.current_level}</span>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-gray-400 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;