import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/axios';
import type { User } from '@/features/auth';
import type { UsersListResponse, CreateUserRequest } from './types';

/**
 * Fetch users list with pagination.
 */
export function useUsers(skip = 0, limit = 50) {
  return useQuery({
    queryKey: ['users', skip, limit],
    queryFn: async (): Promise<UsersListResponse> => {
      const { data } = await api.get<UsersListResponse>('/users', {
        params: { skip, limit },
      });
      return data;
    },
  });
}

/**
 * Create a new user.
 */
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userData: CreateUserRequest): Promise<User> => {
      const { data } = await api.post<User>('/users', userData);
      return data;
    },
    onSuccess: () => {
      // Invalidate users list to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

/**
 * Delete a user.
 */
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (userId: string): Promise<void> => {
      await api.delete(`/users/${userId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

/**
 * Update a user.
 */
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      userId,
      data,
    }: {
      userId: string;
      data: Partial<CreateUserRequest>;
    }): Promise<User> => {
      const { data: user } = await api.patch<User>(
        `/users/${userId}`,
        data
      );
      return user;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
