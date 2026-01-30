import type { User } from '@/features/auth';

export interface UsersListResponse {
  users: User[];
  total: number;
}

export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;
  role: 'user' | 'manager' | 'admin';
}

export const ROLE_LABELS: Record<string, string> = {
  user: 'Tecnico',
  manager: 'Gerente',
  admin: 'Administrador',
  superadmin: 'Super Admin',
};
