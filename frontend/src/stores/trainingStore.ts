import { create } from 'zustand';

interface TrainingState {
  selectedGame: string | null;
  lastScore: number | null;
  lastResult: {
    score: number;
    statGains: Record<string, number>;
    bondGained: number;
    dustEarned: number;
  } | null;
  isPlaying: boolean;
  
  selectGame: (gameId: string) => void;
  startGame: () => void;
  completeGame: (result: {
    score: number;
    statGains: Record<string, number>;
    bondGained: number;
    dustEarned: number;
  }) => void;
  resetGame: () => void;
}

export const useTrainingStore = create<TrainingState>()((set) => ({
  selectedGame: null,
  lastScore: null,
  lastResult: null,
  isPlaying: false,
  
  selectGame: (gameId) => set({ selectedGame: gameId }),
  startGame: () => set({ isPlaying: true }),
  completeGame: (result) =>
    set({
      isPlaying: false,
      lastScore: result.score,
      lastResult: result,
    }),
  resetGame: () =>
    set({
      selectedGame: null,
      lastScore: null,
      lastResult: null,
      isPlaying: false,
    }),
}));
