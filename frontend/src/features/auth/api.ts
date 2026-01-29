import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import { useAuthStore } from './store';
import type { LoginRequest, LoginResponse } from './types';

/**
 * Login mutation hook.
 * Authenticates user and stores auth state.
 */
export function useLogin() {
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((state) => state.setAuth);

  return useMutation({
    mutationFn: async (credentials: LoginRequest): Promise<LoginResponse> => {
      // Use form data format for OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const { data } = await api.post<LoginResponse>(
        '/api/v1/auth/login',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      return data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token);
      queryClient.clear(); // Clear any stale queries
    },
  });
}

/**
 * Logout mutation hook.
 * Clears auth state and server-side refresh token.
 */
export function useLogout() {
  const queryClient = useQueryClient();
  const clearAuth = useAuthStore((state) => state.clearAuth);

  return useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post('/api/v1/auth/logout');
    },
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
    },
    onError: () => {
      // Clear auth even if server call fails
      clearAuth();
      queryClient.clear();
    },
  });
}

/**
 * Refresh token hook.
 * Used on app startup to recover session.
 */
export function useRefreshToken() {
  const setAuth = useAuthStore((state) => state.setAuth);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const setLoading = useAuthStore((state) => state.setLoading);

  return useMutation({
    mutationFn: async (): Promise<LoginResponse> => {
      const { data } = await api.post<LoginResponse>('/api/v1/auth/refresh');
      return data;
    },
    onSuccess: (data) => {
      setAuth(data.user, data.access_token);
    },
    onError: () => {
      clearAuth();
    },
    onSettled: () => {
      setLoading(false);
    },
  });
}
