import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Play, Award, Users, Clock, Activity, Brain } from "lucide-react";

const Home = () => {
  const navigate = useNavigate();

  const [stats, setStats] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const [statsRes] = await Promise.all([
          fetch("http://localhost:5000/me/stats", {
            credentials: "include",
          }),
        ]);

        if (!statsRes.ok) {
          throw new Error("Failed to fetch stats");
        }

        const statsData = await statsRes.json();
        console.log(statsData);

        setStats(statsData);
      } catch (err) {
        console.error("Error loading profile data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  const handlePlayNow = () => {
    navigate("/game");
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { type: "spring", stiffness: 300, damping: 24 },
    },
  };

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="py-12 md:py-20"
      >
        <div className="max-w-5xl mx-auto text-center px-4">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="inline-block bg-primary-700/20 p-4 rounded-full mb-6"
          >
            <Brain size={48} className="text-primary-600" />
          </motion.div>

          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="text-4xl md:text-5xl lg:text-6xl font-display font-bold mb-6 bg-gradient-to-r from-white to-secondary-300 bg-clip-text text-transparent"
          >
            Challenge Your Knowledge
          </motion.h1>

          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="text-xl text-secondary-300 mb-8 max-w-3xl mx-auto"
          >
            Compete with other players in real-time, test your knowledge across
            various categories, and climb the leaderboard to prove you're the
            ultimate quiz master!
          </motion.p>

          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <button
              onClick={handlePlayNow}
              className="btn-primary text-lg px-8 py-3 rounded-full shadow-lg hover:shadow-primary-600/20 transition-all duration-300 animate-pulse"
            >
              <Play size={20} className="mr-2" />
              Play Now
            </button>
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="py-12 bg-secondary-800 rounded-xl"
      >
        <div className="max-w-7xl mx-auto px-4">
          <motion.h2
            variants={itemVariants}
            className="text-2xl md:text-3xl font-display font-bold mb-10 text-center"
          >
            Game Features
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <motion.div
              variants={itemVariants}
              className="bg-secondary-700 rounded-xl p-6 border border-secondary-600 hover:border-primary-700 transition-colors duration-300"
            >
              <div className="bg-primary-700/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Users className="text-primary-500" />
              </div>
              <h3 className="text-xl font-display font-semibold mb-2">
                Multiplayer Matches
              </h3>
              <p className="text-secondary-300">
                Compete in real-time against other players to test your
                knowledge.
              </p>
            </motion.div>

            <motion.div
              variants={itemVariants}
              className="bg-secondary-700 rounded-xl p-6 border border-secondary-600 hover:border-primary-700 transition-colors duration-300"
            >
              <div className="bg-primary-700/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Award className="text-primary-500" />
              </div>
              <h3 className="text-xl font-display font-semibold mb-2">
                Various Categories
              </h3>
              <p className="text-secondary-300">
                Choose from multiple categories including science, history,
                geography, and more.
              </p>
            </motion.div>

            <motion.div
              variants={itemVariants}
              className="bg-secondary-700 rounded-xl p-6 border border-secondary-600 hover:border-primary-700 transition-colors duration-300"
            >
              <div className="bg-primary-700/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Clock className="text-primary-500" />
              </div>
              <h3 className="text-xl font-display font-semibold mb-2">
                Timed Rounds
              </h3>
              <p className="text-secondary-300">
                Answer quickly to earn more points! Each question has a time
                limit.
              </p>
            </motion.div>

            <motion.div
              variants={itemVariants}
              className="bg-secondary-700 rounded-xl p-6 border border-secondary-600 hover:border-primary-700 transition-colors duration-300"
            >
              <div className="bg-primary-700/20 rounded-full w-12 h-12 flex items-center justify-center mb-4">
                <Activity className="text-primary-500" />
              </div>
              <h3 className="text-xl font-display font-semibold mb-2">
                Leaderboards
              </h3>
              <p className="text-secondary-300">
                Climb the ranks and see how you compare to other players
                globally.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Quick Stats */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="py-12"
      >
        <div className="max-w-5xl mx-auto px-4">
          <div className="bg-secondary-800 rounded-xl p-6 border border-secondary-700">
            <h2 className="text-2xl font-display font-bold mb-6 text-center">
              Your Stats
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-secondary-700 rounded-lg p-4 text-center">
                <p className="text-secondary-400 text-sm">Games Played</p>
                <p className="text-2xl font-display font-bold">
                  {stats?.games_played ?? "-"}
                </p>
              </div>

              <div className="bg-secondary-700 rounded-lg p-4 text-center">
                <p className="text-secondary-400 text-sm">Win Rate</p>
                <p className="text-2xl font-display font-bold text-primary-500">
                  {stats?.win_rate ?? "-"}%
                </p>
              </div>

              <div className="bg-secondary-700 rounded-lg p-4 text-center">
                <p className="text-secondary-400 text-sm">Total Score</p>
                <p className="text-2xl font-display font-bold">
                  {stats?.total_score ?? "-"}
                </p>
              </div>

              <div className="bg-secondary-700 rounded-lg p-4 text-center">
                <p className="text-secondary-400 text-sm">Global Rank</p>
                <p className="text-2xl font-display font-bold">
                  #{stats?.rank ?? "-"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </motion.section>
    </div>
  );
};

export default Home;
