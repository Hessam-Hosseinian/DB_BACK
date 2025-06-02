import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Trophy, Medal, ChevronUp, Search, FilterX, Users } from "lucide-react";
import { useAuthStore } from "../store/authStore";

interface LeaderboardEntry {
  id: string;
  rank: number;
  username: string;
  score: number;
  games: number;
  winRate: number;
  avatar: string;
}

const Leaderboard = () => {
  const { user } = useAuthStore();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [filteredLeaderboard, setFilteredLeaderboard] = useState<
    LeaderboardEntry[]
  >([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentFilter, setCurrentFilter] = useState<
    "score" | "games" | "winRate"
  >("score");

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/leaderboard", {
          credentials: "include", // اگر از session استفاده می‌کنید
        });

        if (!response.ok) {
          throw new Error("Failed to fetch leaderboard");
        }

        const data: LeaderboardEntry[] = await response.json();

        // اضافه کردن کاربر فعلی در صورت نیاز
        if (user && !data.some((entry) => entry.username === user.username)) {
          const userEntry: LeaderboardEntry = {
            id: user.id,
            username: user.username,
            score: 1234,
            games: 12,
            winRate: 67,
            avatar:
              user.avatar ||
              `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`,
            rank: 0,
          };
          data.push(userEntry);
        }

        // محاسبه rank بر اساس score
        data.sort((a, b) => b.score - a.score);
        data.forEach((entry, index) => {
          entry.rank = index + 1;
        });

        setLeaderboard(data);
        setFilteredLeaderboard(data);
      } catch (error) {
        console.error("Error fetching leaderboard:", error);
      }
    };

    fetchLeaderboard();
  }, [user]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (value.trim() === "") {
      setFilteredLeaderboard(leaderboard);
    } else {
      const filtered = leaderboard.filter((entry) =>
        entry.username.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredLeaderboard(filtered);
    }
  };

  const handleFilter = (filter: "score" | "games" | "winRate") => {
    setCurrentFilter(filter);

    const sorted = [...filteredLeaderboard].sort(
      (a, b) => b[filter] - a[filter]
    );
    sorted.forEach((entry, index) => {
      entry.rank = index + 1;
    });

    setFilteredLeaderboard(sorted);
  };

  const clearFilters = () => {
    setSearchTerm("");
    setCurrentFilter("score");
    setFilteredLeaderboard(leaderboard);
  };

  const currentUserEntry = user
    ? filteredLeaderboard.find((entry) => entry.username === user.username)
    : null;

  return (
    <div className="py-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-10"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="inline-block bg-primary-700/20 p-3 rounded-full mb-4"
        >
          <Trophy className="h-8 w-8 text-primary-600" />
        </motion.div>
        <h1 className="text-3xl md:text-4xl font-display font-bold mb-2">
          Global Leaderboard
        </h1>
        <p className="text-secondary-400">
          See how you stack up against other quiz masters
        </p>
      </motion.div>

      <div className="bg-secondary-800 rounded-xl p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-secondary-400" />
            </div>
            <input
              type="text"
              placeholder="Search players..."
              value={searchTerm}
              onChange={handleSearch}
              className="input-field pl-10"
            />
          </div>

          <div className="flex space-x-2">
            {["score", "games", "winRate"].map((filter) => (
              <button
                key={filter}
                onClick={() => handleFilter(filter as any)}
                className={`px-3 py-2 rounded-lg transition-colors ${
                  currentFilter === filter
                    ? "bg-primary-700 text-white"
                    : "bg-secondary-700 text-secondary-400 hover:bg-secondary-600"
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}

            {(searchTerm || currentFilter !== "score") && (
              <button
                onClick={clearFilters}
                className="px-3 py-2 bg-secondary-700 text-secondary-400 rounded-lg hover:bg-secondary-600 transition-colors"
              >
                <FilterX size={18} />
              </button>
            )}
          </div>
        </div>
      </div>

      {currentUserEntry && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-secondary-800 border border-primary-700 rounded-xl p-4 mb-6"
        >
          <h3 className="font-display font-semibold mb-3">Your Ranking</h3>
          <div className="flex items-center">
            <div className="w-10 text-center font-bold">
              #{currentUserEntry.rank}
            </div>
            <div className="w-12 h-12 rounded-full bg-secondary-700 border-2 border-primary-600 overflow-hidden mx-3">
              <img
                src={currentUserEntry.avatar}
                alt={currentUserEntry.username}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-grow">
              <p className="font-medium">
                {currentUserEntry.username}{" "}
                <span className="text-primary-500">(You)</span>
              </p>
            </div>
            <div className="hidden md:block w-24 text-center">
              <p className="text-sm text-secondary-400">Games</p>
              <p className="font-medium">{currentUserEntry.games}</p>
            </div>
            <div className="hidden md:block w-24 text-center">
              <p className="text-sm text-secondary-400">Win Rate</p>
              <p className="font-medium">{currentUserEntry.winRate}%</p>
            </div>
            <div className="w-24 text-center">
              <p className="text-sm text-secondary-400">Score</p>
              <p className="font-bold text-primary-500">
                {currentUserEntry.score}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-secondary-800 rounded-xl overflow-hidden"
      >
        {filteredLeaderboard.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-secondary-700">
                  <th className="px-4 py-3 text-left w-16">Rank</th>
                  <th className="px-4 py-3 text-left">Player</th>
                  <th className="px-4 py-3 text-center">Games</th>
                  <th className="px-4 py-3 text-center">Win Rate</th>
                  <th className="px-4 py-3 text-center">Score</th>
                </tr>
              </thead>
              <tbody>
                {filteredLeaderboard.slice(0, 20).map((entry, index) => {
                  const isCurrentUser =
                    user && entry.username === user.username;
                  const isTopThree = entry.rank <= 3;

                  return (
                    <motion.tr
                      key={entry.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.1 * index }}
                      className={`border-b border-secondary-700 ${
                        isCurrentUser ? "bg-primary-900/20" : ""
                      } hover:bg-secondary-700/50 transition-colors`}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center">
                          {isTopThree ? (
                            <div
                              className={`w-8 h-8 flex items-center justify-center rounded-full ${
                                entry.rank === 1
                                  ? "bg-yellow-500/20 text-yellow-500"
                                  : entry.rank === 2
                                  ? "bg-gray-400/20 text-gray-400"
                                  : "bg-amber-800/20 text-amber-700"
                              }`}
                            >
                              <Trophy size={16} />
                            </div>
                          ) : (
                            <span className="font-medium">{entry.rank}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-secondary-700 overflow-hidden mr-3">
                            <img
                              src={entry.avatar}
                              alt={entry.username}
                              className="w-full h-full object-cover"
                            />
                          </div>
                          <span
                            className={`font-medium ${
                              isCurrentUser ? "text-primary-500" : ""
                            }`}
                          >
                            {entry.username}
                            {isCurrentUser && (
                              <span className="ml-2 text-xs">(You)</span>
                            )}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-center">{entry.games}</td>
                      <td className="px-4 py-3 text-center">
                        {entry.winRate}%
                      </td>
                      <td className="px-4 py-3 text-center font-bold">
                        {entry.score}
                      </td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-12 text-center">
            <Users size={48} className="mx-auto mb-4 text-secondary-600" />
            <h3 className="text-xl font-medium mb-2">No players found</h3>
            <p className="text-secondary-400">Try a different search term</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Leaderboard;
