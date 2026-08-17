import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  sessionToken: string | null;
  userEmail: string | null;
  walletAddress: string | null;
  isNewUser: boolean;
  lockdownActive: boolean;
  
  // Actions
  setAuth: (data: {
    userId: string;
    sessionToken: string;
    userEmail: string;
    walletAddress: string;
    isNewUser: boolean;
    lockdownActive: boolean;
  }) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      userId: null,
      sessionToken: null,
      userEmail: null,
      walletAddress: null,
      isNewUser: false,
      lockdownActive: true,
      
      setAuth: (data) =>
        set({
          isAuthenticated: true,
          userId: data.userId,
          sessionToken: data.sessionToken,
          userEmail: data.userEmail,
          walletAddress: data.walletAddress,
          isNewUser: data.isNewUser,
          lockdownActive: data.lockdownActive,
        }),
      
      logout: () =>
        set({
          isAuthenticated: false,
          userId: null,
          sessionToken: null,
          userEmail: null,
          walletAddress: null,
          isNewUser: false,
          lockdownActive: true,
        }),
    }),
    {
      name: 'tektribe-auth',
      // Persist to localStorage (survives page reload)
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          return str ? JSON.parse(str) : null;
        },
        setItem: (name, value) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => {
          localStorage.removeItem(name);
        },
      },
    }
  )
);
