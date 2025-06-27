import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { User, Trophy, Zap, Calendar, Award, TrendingUp, Target } from 'lucide-react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import { statsAPI } from '../../services/api';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserStats();
  }, []);

  const loadUserStats = async () => {
    if (!user) return;
    
    try {
      const userStats = await statsAPI.getUserStats(user.id);
      setStats(userStats);
    } catch (error) {
      console.error('Failed to load user stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressToNextLevel = () => {
    const currentLevel = user?.current_level || 1;
    const currentXP = user?.total_xp || 0;
    const xpForCurrentLevel = (currentLevel - 1) * 1000;
    const xpForNextLevel = currentLevel * 1000;
    const progressXP = currentXP - xpForCurrentLevel;
    const neededXP = xpForNextLevel - xpForCurrentLevel;
    return { progressXP, neededXP, percentage: (progressXP / neededXP) * 100 };
  };

  const { progressXP, neededXP, percentage } = getProgressToNextLevel();

  if (!user) return null;

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">Player Profile</h1>
        <p className="text-gray-300">Your quiz journey and achievements</p>
      </div>

      {/* Profile Header */}
      <Card>
        <div className="p-8">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center">
              <User className="h-12 w-12 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-white mb-2">{user.username}</h2>
              <p className="text-gray-400 mb-4">{user.email}</p>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-orange-400" />
                  <span className="text-white">Level {user.current_level}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Trophy className="h-5 w-5 text-orange-400" />
                  <span className="text-white">{user.total_xp} XP</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-orange-400" />
                  <span className="text-white">Member since 2024</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Level Progress */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-white">Level Progress</h3>
            <span className="text-orange-400 font-medium">
              {progressXP} / {neededXP} XP
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
            <div 
              className="bg-gradient-to-r from-orange-500 to-orange-600 h-4 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(percentage, 100)}%` }}
            ></div>
          </div>
          <p className="text-gray-400 text-sm">
            {neededXP - progressXP} XP needed to reach Level {user.current_level + 1}
          </p>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div className="p-6 text-center">
            <Trophy className="h-8 w-8 text-orange-400 mx-auto mb-3" />
            <div className="text-2xl font-bold text-white mb-1">
              {stats?.games_won || 0}
            </div>
            <p className="text-gray-400 text-sm">Games Won</p>
          </div>
        </Card>

        <Card>
          <div className="p-6 text-center">
            <Target className="h-8 w-8 text-orange-400 mx-auto mb-3" />
            <div className="text-2xl font-bold text-white mb-1">
              {((stats?.games_won || 0) + (stats?.games_lost || 0))}
            </div>
            <p className="text-gray-400 text-sm">Total Games</p>
          </div>
        </Card>

        <Card>
          <div className="p-6 text-center">
            <TrendingUp className="h-8 w-8 text-orange-400 mx-auto mb-3" />
            <div className="text-2xl font-bold text-white mb-1">
              {stats?.win_rate_percentage?.toFixed(1) || '0.0'}%
            </div>
            <p className="text-gray-400 text-sm">Win Rate</p>
          </div>
        </Card>

        <Card>
          <div className="p-6 text-center">
            <Award className="h-8 w-8 text-orange-400 mx-auto mb-3" />
            <div className="text-2xl font-bold text-white mb-1">
              {Math.floor((user.total_xp || 0) / 100)}
            </div>
            <p className="text-gray-400 text-sm">Achievements</p>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {[
              { type: 'win', opponent: 'QuizMaster', points: 450, time: '2 hours ago' },
              { type: 'loss', opponent: 'BrainBox', points: 380, time: '1 day ago' },
              { type: 'win', opponent: 'Smarty', points: 520, time: '2 days ago' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-black/20 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    activity.type === 'win' ? 'bg-green-400' : 'bg-red-400'
                  }`}></div>
                  <div>
                    <p className="text-white font-medium">
                      {activity.type === 'win' ? 'Victory' : 'Defeat'} vs {activity.opponent}
                    </p>
                    <p className="text-gray-400 text-sm">{activity.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-orange-400 font-bold">{activity.points} pts</div>
                  <div className={`text-sm ${
                    activity.type === 'win' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {activity.type === 'win' ? '+' : '-'}{Math.floor(activity.points / 10)} XP
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Achievements */}
      <Card>
        <div className="p-6">
          <h3 className="text-xl font-bold text-white mb-4">Achievements</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'First Victory', description: 'Win your first game', earned: true },
              { name: 'Quiz Master', description: 'Win 10 games', earned: true },
              { name: 'Speed Demon', description: 'Answer 10 questions in under 5 seconds', earned: false },
              { name: 'Knowledge Seeker', description: 'Play 50 games', earned: false },
              { name: 'Perfect Round', description: 'Answer all questions correctly in a round', earned: true },
              { name: 'Category Expert', description: 'Win 5 games in the same category', earned: false },
            ].map((achievement, index) => (
              <div key={index} className={`p-4 rounded-lg border-2 ${
                achievement.earned 
                  ? 'bg-orange-500/10 border-orange-500/30' 
                  : 'bg-gray-500/10 border-gray-500/20'
              }`}>
                <div className="flex items-center space-x-3 mb-2">
                  <Award className={`h-6 w-6 ${
                    achievement.earned ? 'text-orange-400' : 'text-gray-500'
                  }`} />
                  <h4 className={`font-bold ${
                    achievement.earned ? 'text-white' : 'text-gray-500'
                  }`}>
                    {achievement.name}
                  </h4>
                </div>
                <p className={`text-sm ${
                  achievement.earned ? 'text-gray-300' : 'text-gray-500'
                }`}>
                  {achievement.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Profile;