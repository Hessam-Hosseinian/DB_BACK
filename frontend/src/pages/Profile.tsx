import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAuthStore } from "../store/authStore";
import {
  Trophy,
  User,
  Award,
  PieChart,
  BarChart3,
  BookOpen,
  TrendingUp,
  Calendar,
  Clock,
  Edit3,
} from "lucide-react";

const Profile = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState("stats");

  // const [profile, setprofile] = useState<any | null>(null);
  const [stats, setStats] = useState<any | null>(null);
  const [achievementsData, setAchievementsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<any | null>(null);
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        // statsRes, achievementsRes,
        const [profileRes, statsRes] = await Promise.all([
          fetch("http://localhost:5000/profile", {
            credentials: "include",
          }),
          fetch("http://localhost:5000/me/stats", {
            credentials: "include",
          }),
          // fetch("http://localhost:5000/me/achievements", {
          //   credentials: "include",
          // }),
        ]);

        // if (!statsRes.ok || !achievementsRes.ok || !profileRes.ok) {
        //   throw new Error("Failed to fetch one of the profile data parts");
        // }

        const statsData = await statsRes.json();
        // console.log(statsData);
        // const achievements = await achievementsRes.json();
        const profileData = await profileRes.json();

        setStats(statsData);
        // setAchievementsData(achievements);
        setProfile(profileData);
      } catch (err) {
        console.error("Error loading profile data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  const tabs = [
    { id: "stats", label: "Statistics", icon: <PieChart size={18} /> },
    { id: "achievements", label: "Achievements", icon: <Award size={18} /> },
  ];

  const renderContent = () => {
    if (loading)
      return <p className="text-center text-secondary-400">Loading...</p>;

    switch (activeTab) {
      case "stats":
        return (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-secondary-800 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <Trophy size={18} className="text-primary-500 mr-2" />
                  <span className="text-secondary-400 text-sm">Games Won</span>
                </div>
                <p className="text-2xl font-bold">{stats?.wins ?? "-"}</p>
                <p className="text-xs text-secondary-400">
                  out of {stats?.games_played ?? "-"} games
                </p>
              </div>

              <div className="bg-secondary-800 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <BarChart3 size={18} className="text-primary-500 mr-2" />
                  <span className="text-secondary-400 text-sm">Win Rate</span>
                </div>
                <p className="text-2xl font-bold">
                  {stats
                    ? Math.round((stats.wins / stats.games_played) * 100) + "%"
                    : "-"}
                </p>
                <p className="text-xs text-secondary-400">
                  {stats?.wins} wins / {stats?.games_played} games
                </p>
              </div>

              <div className="bg-secondary-800 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <BookOpen size={18} className="text-primary-500 mr-2" />
                  <span className="text-secondary-400 text-sm">Questions</span>
                </div>
                <p className="text-2xl font-bold">
                  {stats
                    ? Math.round(
                        (stats.correct_answers / stats.total_answers) * 100
                      ) + "%"
                    : "-"}
                </p>
                <p className="text-xs text-secondary-400">
                  {stats?.correct_answers ?? 0} correct /{" "}
                  {stats?.total_answers ?? 0} total
                </p>
              </div>

              <div className="bg-secondary-800 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <TrendingUp size={18} className="text-primary-500 mr-2" />
                  <span className="text-secondary-400 text-sm">XP</span>
                </div>
                <p className="text-2xl font-bold">{stats?.xp ?? 0}</p>
                <p className="text-xs text-secondary-400">
                  Level {Math.floor((stats?.xp ?? 0) / 1000)}
                </p>
              </div>
            </div>
          </motion.div>
        );

      case "achievements":
        return (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {achievementsData.map((achievement) => (
              <motion.div
                key={achievement.name}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className={`bg-secondary-800 rounded-lg p-4 border-l-4 ${
                  achievement.earned_at
                    ? "border-primary-600"
                    : "border-secondary-700"
                }`}
              >
                <div className="flex items-start">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center mr-3 ${
                      achievement.earned_at
                        ? "bg-primary-700/20 text-primary-500"
                        : "bg-secondary-700 text-secondary-400"
                    }`}
                  >
                    <Award size={18} />
                  </div>
                  <div className="flex-grow">
                    <h4 className="font-medium">{achievement.name}</h4>
                    <p className="text-sm text-secondary-400 mb-2">
                      {achievement.description}
                    </p>

                    {achievement.earned_at ? (
                      <p className="text-xs text-primary-500 flex items-center">
                        <Trophy size={12} className="mr-1" />
                        Completed on{" "}
                        {new Date(achievement.earned_at).toLocaleDateString()}
                      </p>
                    ) : (
                      <div>
                        <div className="w-full bg-secondary-700 rounded-full h-1.5 mb-1">
                          <div
                            className="bg-primary-600 h-1.5 rounded-full"
                            style={{ width: `${achievement.progress || 0}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-secondary-400">
                          Progress: {achievement.progress || 0}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="py-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="bg-secondary-800 rounded-xl overflow-hidden mb-8"
      >
        <div className="h-32 bg-gradient-to-r from-primary-800 to-primary-600 relative">
          <button className="absolute top-4 right-4 bg-white/10 backdrop-blur-sm text-white rounded-full p-2 hover:bg-white/20 transition-colors">
            <Edit3 size={18} />
          </button>
        </div>

        <div className="px-6 pb-6 pt-14 relative">
          <div className="absolute -top-12 left-6 w-24 h-24 rounded-full bg-secondary-800 p-1.5">
            <img
              src={
                user?.avatar ||
                `https://api.dicebear.com/7.x/avataaars/svg?seed=${
                  user?.username || "User"
                }`
              }
              alt="Profile"
              className="w-full h-full rounded-full bg-secondary-700 object-cover"
            />
          </div>

          <div className="ml-28">
            <h1 className="text-2xl font-display font-bold">
              {user?.username || "User"}
            </h1>
            <p className="text-secondary-400">
              {profile?.email || "user@example.com"}
            </p>
            <p className="text-secondary-400">
              {profile?.registered_at
                ? new Date(profile.registered_at).toLocaleString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    hour12: false,
                  })
                : "June 2, 2025 at 18:09"}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="text-center">
              <p className="text-2xl font-bold">{stats?.games_played ?? "-"}</p>
              <p className="text-sm text-secondary-400">Games</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-500">
                {stats?.wins ?? "-"}
              </p>
              <p className="text-sm text-secondary-400">Wins</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">#{stats?.rank ?? "-"}</p>
              <p className="text-sm text-secondary-400">Rank</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Tabs Navigation */}
      <div className="bg-secondary-800 rounded-xl overflow-hidden mb-6">
        <div className="flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-grow py-4 px-4 flex items-center justify-center transition-colors ${
                activeTab === tab.id
                  ? "bg-primary-700 text-white"
                  : "hover:bg-secondary-700 text-secondary-400"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        {renderContent()}
      </motion.div>
    </div>
  );
};

export default Profile;
