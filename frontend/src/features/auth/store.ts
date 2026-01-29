import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { AuthState, User } from './types';

/**
 * Zustand auth store with persistence.
 *
 * - User info persisted to localStorage (survives refresh)
 * - Access token stored in memory only (security)
 * - On refresh, token is recovered via /auth/refresh endpoint
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,

      setAuth: (user: User, accessToken: string) =>
        set({
          user,
          accessToken,
          isAuthenticated: true,
          isLoading: false,
        }),

      clearAuth: () =>
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      setLoading: (loading: boolean) =>
        set({ isLoading: loading }),

      setAccessToken: (token: string) =>
        set({ accessToken: token }),
    }),
    {
      name: 'smarthand-auth',
      storage: createJSONStorage(() => localStorage),
      // Only persist user info, NOT access token (security)
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      // On rehydration, set loading to trigger token refresh
      onRehydrateStorage: () => (state) => {
        if (state) {
          // If we have persisted user but no token, we need to refresh
          if (state.isAuthenticated && !state.accessToken) {
            state.isLoading = true;
          } else {
            state.isLoading = false;
          }
        }
      },
    }
  )
);
