import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Brain, LogIn, AlertCircle, Loader2 } from "lucide-react";
import { useAuthStore } from "../store/authStore";

const Login = () => {
  const [username, setUsername] = useState("");

  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(username, password);
      navigate("/profile");
    } catch (err) {
      setError("Invalid username or password");
    } finally {
      setIsLoading(false);
    }
  };

  // For demo purposes, provide a quick login option
  const handleDemoLogin = async () => {
    setUsername("user");
    setPassword("password1234PA");
    setIsLoading(true);

    try {
      await login("user", "password1234PA");
      navigate("/");
    } catch (err) {
      setError("Something went wrong with demo login");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-secondary-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-secondary-800 rounded-xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-800 to-primary-600 p-6 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{
                type: "spring",
                stiffness: 260,
                damping: 20,
                delay: 0.2,
              }}
              className="inline-block bg-white/10 p-3 rounded-full backdrop-blur-sm mb-3"
            >
              <Brain className="h-10 w-10 text-white" />
            </motion.div>
            <h1 className="text-2xl font-display font-bold text-white">
              Quiz Challenge
            </h1>
            <p className="text-primary-100 mt-1">Login to your account</p>
          </div>

          {/* Form */}
          <div className="p-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="bg-error/10 text-error flex items-center gap-2 px-4 py-3 rounded-lg mb-4"
              >
                <AlertCircle size={18} />
                <span>{error}</span>
              </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-secondary-300 mb-1"
                >
                  Email
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="input-field"
                  placeholder="Enter your username"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-secondary-300 mb-1"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field"
                  placeholder="Enter your password"
                  required
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full flex items-center justify-center"
                >
                  {isLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  ) : (
                    <LogIn className="h-5 w-5 mr-2" />
                  )}
                  {isLoading ? "Logging in..." : "Login"}
                </button>
              </div>
            </form>

            <div className="mt-4">
              <button
                onClick={handleDemoLogin}
                className="btn-outline w-full"
                disabled={isLoading}
              >
                Quick Demo Login
              </button>
            </div>

            <div className="mt-6 text-center">
              <p className="text-secondary-400">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="text-primary-500 hover:underline"
                >
                  Register
                </Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
