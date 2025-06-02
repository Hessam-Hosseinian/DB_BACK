import { create } from 'zustand';

export interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
}

export interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  category: string;
}

export interface GamePlayer {
  id: string;
  username: string;
  avatar: string;
  score: number;
}

export type GameStatus = 'idle' | 'finding-opponent' | 'category-selection' | 'playing' | 'round-results' | 'game-over';
export type MatchStatus = 'waiting' | 'matched' | 'playing' | 'completed';

interface GameState {
  status: GameStatus;
  matchStatus: MatchStatus;
  opponent: GamePlayer | null;
  categories: Category[];
  availableCategories: Category[];
  selectedCategory: Category | null;
  currentRound: number;
  questions: Question[];
  currentQuestionIndex: number;
  selectedAnswer: number | null;
  playerScore: number;
  opponentScore: number;
  timer: number;
  roundResults: {
    playerCorrect: boolean[];
    opponentCorrect: boolean[];
  };
  
  // Actions
  findOpponent: () => void;
  cancelMatchmaking: () => void;
  selectCategory: (categoryId: string) => void;
  selectAnswer: (answerIndex: number) => void;
  nextQuestion: () => void;
  startNextRound: () => void;
  resetGame: () => void;
}

// Mock categories
const mockCategories: Category[] = [
  { 
    id: '1', 
    name: 'Science', 
    icon: '🔬', 
    description: 'Test your knowledge of scientific facts and discoveries' 
  },
  { 
    id: '2', 
    name: 'History', 
    icon: '📜', 
    description: 'Journey through time with historical questions' 
  },
  { 
    id: '3', 
    name: 'Geography', 
    icon: '🌍', 
    description: 'Explore the world with geography questions' 
  },
  { 
    id: '4', 
    name: 'Entertainment', 
    icon: '🎬', 
    description: 'Test your knowledge of movies, music, and pop culture' 
  },
  { 
    id: '5', 
    name: 'Sports', 
    icon: '⚽', 
    description: 'Challenge yourself with sports trivia' 
  },
];

// Mock questions generator
const generateMockQuestions = (category: string, count: number): Question[] => {
  const questions: Question[] = [];
  
  for (let i = 0; i < count; i++) {
    questions.push({
      id: `${category}-${i}`,
      question: `This is a sample ${category} question ${i + 1}?`,
      options: [
        `${category} answer option 1`,
        `${category} answer option 2`,
        `${category} answer option 3`,
        `${category} answer option 4`,
      ],
      correctAnswer: Math.floor(Math.random() * 4),
      category,
    });
  }
  
  return questions;
};

export const useGameStore = create<GameState>((set, get) => ({
  status: 'idle',
  matchStatus: 'waiting',
  opponent: null,
  categories: mockCategories,
  availableCategories: [],
  selectedCategory: null,
  currentRound: 0,
  questions: [],
  currentQuestionIndex: 0,
  selectedAnswer: null,
  playerScore: 0,
  opponentScore: 0,
  timer: 15,
  roundResults: {
    playerCorrect: [],
    opponentCorrect: [],
  },
  
  findOpponent: () => {
    set({ status: 'finding-opponent', matchStatus: 'waiting' });
    
    // Simulate finding an opponent after a delay
    setTimeout(() => {
      const mockOpponent: GamePlayer = {
        id: '2',
        username: 'Opponent',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Opponent',
        score: 0,
      };
      
      // Select 3 random categories to offer
      const shuffled = [...mockCategories].sort(() => 0.5 - Math.random());
      const randomCategories = shuffled.slice(0, 3);
      
      set({
        opponent: mockOpponent,
        matchStatus: 'matched',
        status: 'category-selection',
        availableCategories: randomCategories,
        currentRound: 1,
      });
    }, 3000);
  },
  
  cancelMatchmaking: () => {
    set({ status: 'idle', matchStatus: 'waiting', opponent: null });
  },
  
  selectCategory: (categoryId: string) => {
    const { availableCategories } = get();
    const category = availableCategories.find(c => c.id === categoryId);
    
    if (category) {
      // Generate 3 questions for the selected category
      const questions = generateMockQuestions(category.name, 3);
      
      set({
        selectedCategory: category,
        status: 'playing',
        questions,
        currentQuestionIndex: 0,
        selectedAnswer: null,
        timer: 15,
        matchStatus: 'playing',
      });
    }
  },
  
  selectAnswer: (answerIndex: number) => {
    const { questions, currentQuestionIndex, roundResults, playerScore } = get();
    const currentQuestion = questions[currentQuestionIndex];
    const isCorrect = answerIndex === currentQuestion.correctAnswer;
    
    // Update player results for this round
    const updatedPlayerCorrect = [...roundResults.playerCorrect];
    updatedPlayerCorrect[currentQuestionIndex] = isCorrect;
    
    // Generate random result for opponent
    const opponentCorrect = Math.random() > 0.5;
    const updatedOpponentCorrect = [...roundResults.opponentCorrect];
    updatedOpponentCorrect[currentQuestionIndex] = opponentCorrect;
    
    // Update scores
    const newPlayerScore = isCorrect ? playerScore + 10 : playerScore;
    const newOpponentScore = get().opponentScore + (opponentCorrect ? 10 : 0);
    
    set({
      selectedAnswer: answerIndex,
      roundResults: {
        playerCorrect: updatedPlayerCorrect,
        opponentCorrect: updatedOpponentCorrect,
      },
      playerScore: newPlayerScore,
      opponentScore: newOpponentScore,
    });
    
    // Move to next question after a delay
    setTimeout(() => {
      get().nextQuestion();
    }, 2000);
  },
  
  nextQuestion: () => {
    const { currentQuestionIndex, questions } = get();
    const nextIndex = currentQuestionIndex + 1;
    
    if (nextIndex < questions.length) {
      // Move to the next question
      set({
        currentQuestionIndex: nextIndex,
        selectedAnswer: null,
        timer: 15,
      });
    } else {
      // End of round
      set({
        status: 'round-results',
      });
    }
  },
  
  startNextRound: () => {
    const { currentRound } = get();
    
    if (currentRound < 5) {
      // Select 3 new random categories to offer
      const shuffled = [...mockCategories].sort(() => 0.5 - Math.random());
      const randomCategories = shuffled.slice(0, 3);
      
      set({
        currentRound: currentRound + 1,
        status: 'category-selection',
        availableCategories: randomCategories,
        roundResults: {
          playerCorrect: [],
          opponentCorrect: [],
        },
      });
    } else {
      // Game over after 5 rounds
      set({
        status: 'game-over',
        matchStatus: 'completed',
      });
    }
  },
  
  resetGame: () => {
    set({
      status: 'idle',
      matchStatus: 'waiting',
      opponent: null,
      selectedCategory: null,
      currentRound: 0,
      questions: [],
      currentQuestionIndex: 0,
      selectedAnswer: null,
      playerScore: 0,
      opponentScore: 0,
      timer: 15,
      roundResults: {
        playerCorrect: [],
        opponentCorrect: [],
      },
    });
  },
}));