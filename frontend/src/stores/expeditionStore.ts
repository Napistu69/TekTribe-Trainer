import { create } from 'zustand';

interface ExpeditionState {
  activeExpeditions: any[];
  expeditionHistory: any[];
  selectedBiome: string | null;
  selectedCompanion: string | null;
  selectedDuration: string;
  
  setActiveExpeditions: (expeditions: any[]) => void;
  setExpeditionHistory: (history: any[]) => void;
  setSelectedBiome: (biome: string | null) => void;
  setSelectedCompanion: (companion: string | null) => void;
  setSelectedDuration: (duration: string) => void;
}

export const useExpeditionStore = create<ExpeditionState>()((set) => ({
  activeExpeditions: [],
  expeditionHistory: [],
  selectedBiome: 'verdant_hollow',
  selectedCompanion: null,
  selectedDuration: '2h',
  
  setActiveExpeditions: (expeditions) => set({ activeExpeditions: expeditions }),
  setExpeditionHistory: (history) => set({ expeditionHistory: history }),
  setSelectedBiome: (biome) => set({ selectedBiome: biome }),
  setSelectedCompanion: (companion) => set({ selectedCompanion: companion }),
  setSelectedDuration: (duration) => set({ selectedDuration: duration }),
}));
