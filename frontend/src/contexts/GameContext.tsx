import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Game {
  id: number;
  type: 'duel' | 'multiplayer';
  status: 'pending' | 'active' | 'completed';
  participants: any[];
  current_round: number;
  total_rounds: number;
}

interface GameContextType {
  currentGame: Game | null;
  setCurrentGame: (game: Game | null) => void;
  gameMode: 'duel' | 'multiplayer' | null;
  setGameMode: (mode: 'duel' | 'multiplayer' | null) => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
};

interface GameProviderProps {
  children: ReactNode;
}

export const GameProvider: React.FC<GameProviderProps> = ({ children }) => {
  const [currentGame, setCurrentGame] = useState<Game | null>(null);
  const [gameMode, setGameMode] = useState<'duel' | 'multiplayer' | null>(null);

  return (
    <GameContext.Provider value={{ currentGame, setCurrentGame, gameMode, setGameMode }}>
      {children}
    </GameContext.Provider>
  );
};