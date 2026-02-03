import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api/v1`;

/**
 * Configured Axios instance for API requests.
 *
 * Features:
 * - Sends access token in Authorization header
 * - Sends cookies with requests (for refresh token)
 * - Auto-refreshes token on 401 response
 * - Redirects to login on refresh failure
 */
export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Send cookies (refresh token)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Track if we're currently refreshing to prevent infinite loops
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

// Lazy import to avoid circular dependency
let authStoreModule: typeof import('@/features/auth/store') | null = null;

const getAuthStore = async () => {
  if (!authStoreModule) {
    authStoreModule = await import('@/features/auth/store');
  }
  return authStoreModule.useAuthStore;
};

// Request interceptor - add access token
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const useAuthStore = await getAuthStore();
      const accessToken = useAuthStore.getState().accessToken;

      if (accessToken && config.headers) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
    } catch {
      // Auth store not yet available, proceed without token
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Only retry on 401 and if we haven't already retried
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Don't retry refresh endpoint itself
    if (originalRequest.url?.includes('/auth/refresh')) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // If refresh is in progress, queue this request
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(api(originalRequest));
          },
          reject: (err: Error) => {
            reject(err);
          },
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      // Attempt to refresh token
      const { data } = await axios.post<{
        user: unknown;
        access_token: string;
      }>(
        `${API_URL}/auth/refresh`,
        {},
        { withCredentials: true }
      );

      // Update auth store with new token
      const useAuthStore = await getAuthStore();
      useAuthStore.getState().setAccessToken(data.access_token);

      // Process queued requests with new token
      processQueue(null, data.access_token);

      // Retry original request with new token
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      }
      return api(originalRequest);
    } catch (refreshError) {
      // Refresh failed - clear auth and redirect to login
      processQueue(refreshError as Error);

      try {
        const useAuthStore = await getAuthStore();
        useAuthStore.getState().clearAuth();
      } catch {
        // Auth store not available
      }

      // Redirect to login (preserve current path for redirect after login)
      const currentPath = window.location.pathname;
      if (currentPath !== '/login') {
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
      }

      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
