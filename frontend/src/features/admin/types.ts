import type { User } from '@/features/auth';

export interface UsersListResponse {
  users: User[];
  total: number;
}

export interface CreateUserRequest {
  email: string;
  full_name: string;
  password: string;
  role: 'viewer' | 'technician' | 'project_manager' | 'tenant_admin';
}

export const ROLE_LABELS: Record<string, string> = {
  viewer: 'Visualizador',
  technician: 'Tecnico',
  project_manager: 'Gerente de Projeto',
  tenant_admin: 'Administrador',
  superadmin: 'Super Admin',
};
