import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  username: string;
  email?: string;
  avatar?: string;
  is_admin?: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      login: async (username, password) => {
        const res = await fetch("http://localhost:5000/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ username, password }),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data?.error || "Login failed");

        set({
          user: {
            id: data.user_id.toString(),
            username: data.username,
            is_admin: data.is_admin,
            avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.username}`,
          },
          isAuthenticated: true,
        });
      },

      register: async (username, email, password) => {
        const res = await fetch("http://localhost:5000/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ username, email, password }),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data?.error || "Registration failed");

        set({
          user: {
            id: data.user_id.toString(),
            username: data.username,

            avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.username}`,
          },
          isAuthenticated: true,
        });
      },

      logout: async () => {
        await fetch("http://localhost:5000/logout", {
          method: "POST",
          credentials: "include",
        });
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: "auth-storage",
    }
  )
);
