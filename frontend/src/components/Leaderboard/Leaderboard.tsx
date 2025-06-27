import React, { useState, useEffect } from 'react';
import { Trophy, Medal, Crown, TrendingUp, Calendar } from 'lucide-react';
import Card from '../UI/Card';
import Button from '../UI/Button';
import { statsAPI } from '../../services/api';

interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  score: number;
  games_played: number;
  win_rate: number;
}

const Leaderboard: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [scope, setScope] = useState<'alltime' | 'weekly' | 'monthly'>('alltime');

  useEffect(() => {
    loadLeaderboard();
  }, [scope]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const data = await statsAPI.getLeaderboard(scope, 50);
      setLeaderboard(data.map((entry: any, index: number) => ({
        ...entry,
        rank: index + 1
      })));
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-6 w-6 text-yellow-400" />;
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />;
      case 3:
        return <Medal className="h-6 w-6 text-orange-600" />;
      default:
        return <span className="text-gray-400 font-bold">#{rank}</span>;
    }
  };

  const getRankBackground = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border-yellow-500/30';
      case 2:
        return 'bg-gradient-to-r from-gray-400/20 to-gray-500/20 border-gray-400/30';
      case 3:
        return 'bg-gradient-to-r from-orange-500/20 to-orange-600/20 border-orange-500/30';
      default:
        return 'bg-black/20 border-gray-600/20';
    }
  };

  const getScopeLabel = (scope: string) => {
    switch (scope) {
      case 'weekly':
        return 'This Week';
      case 'monthly':
        return 'This Month';
      default:
        return 'All Time';
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-2">Leaderboard</h1>
        <p className="text-gray-300">See how you rank against other players</p>
      </div>

      {/* Scope Selector */}
      <div className="flex justify-center">
        <div className="flex bg-black/30 rounded-lg p-1 border border-gray-600/30">
          {['alltime', 'monthly', 'weekly'].map((period) => (
            <Button
              key={period}
              variant={scope === period ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setScope(period as any)}
              className="min-w-24"
            >
              <Calendar className="h-4 w-4 mr-2" />
              {getScopeLabel(period)}
            </Button>
          ))}
        </div>
      </div>

      {/* Top 3 Podium */}
      {leaderboard.length >= 3 && (
        <div className="grid grid-cols-3 gap-4 max-w-3xl mx-auto">
          {/* 2nd Place */}
          <Card className="bg-gradient-to-r from-gray-400/20 to-gray-500/20 border-gray-400/30">
            <div className="p-6 text-center">
              <div className="w-16 h-16 bg-gray-400 rounded-full flex items-center justify-center mx-auto mb-4">
                <Medal className="h-8 w-8 text-black" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{leaderboard[1].username}</h3>
              <p className="text-2xl font-bold text-gray-400 mb-2">{leaderboard[1].score}</p>
              <p className="text-sm text-gray-400">{leaderboard[1].win_rate.toFixed(1)}% WR</p>
            </div>
          </Card>

          {/* 1st Place */}
          <Card className="bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 border-yellow-500/30 transform scale-105">
            <div className="p-6 text-center">
              <div className="w-20 h-20 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Crown className="h-10 w-10 text-black" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">{leaderboard[0].username}</h3>
              <p className="text-3xl font-bold text-yellow-400 mb-2">{leaderboard[0].score}</p>
              <p className="text-sm text-gray-300">{leaderboard[0].win_rate.toFixed(1)}% WR</p>
            </div>
          </Card>

          {/* 3rd Place */}
          <Card className="bg-gradient-to-r from-orange-500/20 to-orange-600/20 border-orange-500/30">
            <div className="p-6 text-center">
              <div className="w-16 h-16 bg-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Medal className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{leaderboard[2].username}</h3>
              <p className="text-2xl font-bold text-orange-400 mb-2">{leaderboard[2].score}</p>
              <p className="text-sm text-gray-400">{leaderboard[2].win_rate.toFixed(1)}% WR</p>
            </div>
          </Card>
        </div>
      )}

      {/* Full Leaderboard */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white flex items-center">
              <Trophy className="h-6 w-6 text-orange-400 mr-2" />
              {getScopeLabel(scope)} Rankings
            </h2>
            <div className="text-sm text-gray-400">
              {leaderboard.length} players
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin w-8 h-8 border-2 border-orange-500 border-t-transparent rounded-full mx-auto"></div>
            </div>
          ) : (
            <div className="space-y-2">
              {leaderboard.map((entry) => (
                <div
                  key={entry.user_id}
                  className={`flex items-center justify-between p-4 rounded-lg border transition-all duration-200 hover:scale-102 ${getRankBackground(entry.rank)}`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 flex items-center justify-center">
                      {getRankIcon(entry.rank)}
                    </div>
                    <div>
                      <h3 className="text-white font-semibold text-lg">{entry.username}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-400">
                        <span>{entry.games_played} games</span>
                        <span>{entry.win_rate.toFixed(1)}% win rate</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-orange-400">{entry.score}</div>
                    <div className="text-sm text-gray-400">points</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Leaderboard;