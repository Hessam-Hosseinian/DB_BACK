const API_BASE_URL = 'http://localhost:5000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Network error' }));
    throw new APIError(response.status, error.error || 'Unknown error');
  }
  return response.json();
};

export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    });
    return handleResponse(response);
  },

  register: async (username: string, email: string, password: string) => {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, email, password }),
    });
    return handleResponse(response);
  },

  logout: async () => {
    const response = await fetch(`${API_BASE_URL}/users/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    return handleResponse(response);
  },

  getProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/users/profile`, {
      credentials: 'include',
    });
    return handleResponse(response);
  },
};

export const gameAPI = {
  createGame: async (gameTypeId: number, participantIds: number[]) => {
    const response = await fetch(`${API_BASE_URL}/games`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        game_type_id: gameTypeId,
        creator_id: participantIds[0],
        participant_ids: participantIds,
      }),
    });
    return handleResponse(response);
  },

  joinQueue: async (userId: number, gameTypeId: number) => {
    const response = await fetch(`${API_BASE_URL}/games/queue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ user_id: userId, game_type_id: gameTypeId }),
    });
    return handleResponse(response);
  },

  getCategories: async () => {
    const response = await fetch(`${API_BASE_URL}/categories`, {
      credentials: 'include',
    });
    return handleResponse(response);
  },
};

export const statsAPI = {
  getLeaderboard: async (scope: string = 'alltime', limit: number = 10) => {
    const response = await fetch(`${API_BASE_URL}/leaderboards?scope=${scope}&limit=${limit}`, {
      credentials: 'include',
    });
    return handleResponse(response);
  },

  getUserStats: async (userId: number) => {
    const response = await fetch(`${API_BASE_URL}/stats/user-winloss/${userId}`, {
      credentials: 'include',
    });
    return handleResponse(response);
  },
};