import { create } from 'zustand';

interface EconomyState {
  dust: number;
  shard: number;
  cuboid: number;
  ele: number;
  transactions: any[];
  
  setBalance: (data: { dust: number; shard?: number; cuboid?: number; ele?: number }) => void;
  setTransactions: (transactions: any[]) => void;
}

export const useEconomyStore = create<EconomyState>()((set) => ({
  dust: 0,
  shard: 0,
  cuboid: 0,
  ele: 0,
  transactions: [],
  
  setBalance: (data) => set({
    dust: data.dust,
    shard: data.shard ?? 0,
    cuboid: data.cuboid ?? 0,
    ele: data.ele ?? 0,
  }),
  setTransactions: (transactions) => set({ transactions }),
}));
