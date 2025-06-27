import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import { Sword, Users, Trophy, Zap, Play, TrendingUp } from 'lucide-react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import { statsAPI } from '../../services/api';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { setGameMode } = useGame();
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [userStats, topPlayers] = await Promise.all([
        statsAPI.getUserStats(user?.id || 0),
        statsAPI.getLeaderboard('alltime', 5)
      ]);
      setStats(userStats);
      setLeaderboard(topPlayers);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleGameModeSelect = (mode: 'duel' | 'multiplayer') => {
    setGameMode(mode);
    navigate('/game-lobby');
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">
          Welcome back, <span className="text-orange-400">{user?.username}</span>!
        </h1>
        <p className="text-gray-300 text-lg">Ready to challenge your knowledge?</p>
      </div>

      {/* Game Mode Selection */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="group hover:scale-105 transition-transform duration-300 cursor-pointer">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Sword className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Duel Mode</h3>
            <p className="text-gray-300 mb-4">1v1 quiz battle with 5 rounds of strategic category selection</p>
            <Button
              variant="primary"
              onClick={() => handleGameModeSelect('duel')}
              className="w-full"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Duel
            </Button>
          </div>
        </Card>

        <Card className="group hover:scale-105 transition-transform duration-300 cursor-pointer">
          <div className="text-center p-6">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Users className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">Multiplayer</h3>
            <p className="text-gray-300 mb-4">Group quiz with 10 questions across various categories</p>
            <Button
              variant="secondary"
              onClick={() => handleGameModeSelect('multiplayer')}
              className="w-full"
            >
              <Play className="h-4 w-4 mr-2" />
              Join Group
            </Button>
          </div>
        </Card>
      </div>

      {/* Stats Overview */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Your Level</h3>
              <Zap className="h-6 w-6 text-orange-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              Level {user?.current_level}
            </div>
            <p className="text-gray-400">{user?.total_xp} XP</p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Win Rate</h3>
              <Trophy className="h-6 w-6 text-orange-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              {stats?.win_rate_percentage?.toFixed(1) || '0.0'}%
            </div>
            <p className="text-gray-400">
              {stats?.games_won || 0} wins / {(stats?.games_won || 0) + (stats?.games_lost || 0)} games
            </p>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Rank</h3>
              <TrendingUp className="h-6 w-6 text-orange-400" />
            </div>
            <div className="text-3xl font-bold text-white mb-2">
              #{leaderboard.findIndex(p => p.username === user?.username) + 1 || 'N/A'}
            </div>
            <p className="text-gray-400">Global ranking</p>
          </div>
        </Card>
      </div>

      {/* Top Players Preview */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Top Players</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/leaderboard')}
              className="text-orange-400 hover:text-orange-300"
            >
              View All
            </Button>
          </div>
          <div className="space-y-3">
            {leaderboard.slice(0, 3).map((player, index) => (
              <div key={player.user_id} className="flex items-center justify-between p-3 bg-black/20 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    index === 0 ? 'bg-yellow-500 text-black' :
                    index === 1 ? 'bg-gray-400 text-black' :
                    'bg-orange-600 text-white'
                  }`}>
                    {index + 1}
                  </div>
                  <span className="text-white font-medium">{player.username}</span>
                </div>
                <div className="text-right">
                  <div className="text-orange-400 font-bold">{player.score}</div>
                  <div className="text-gray-400 text-sm">{player.win_rate.toFixed(1)}% WR</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;