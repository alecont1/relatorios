/**
 * Role hierarchy (highest to lowest privilege):
 * - superadmin: Global system admin, tenant_id = NULL
 * - tenant_admin: Admin of a specific tenant
 * - project_manager: Manager of specific projects
 * - technician: Field technician (default)
 * - viewer: Read-only access
 */
export type UserRole = 'superadmin' | 'tenant_admin' | 'project_manager' | 'technician' | 'viewer';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  tenant_id: string | null; // Nullable for superadmin users
  is_active: boolean;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, accessToken: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
  setAccessToken: (token: string) => void;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  token_type: string;
}

/**
 * Role hierarchy levels for permission checks.
 * Higher number = more privilege.
 */
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  superadmin: 100,
  tenant_admin: 80,
  project_manager: 60,
  technician: 40,
  viewer: 20,
};

/**
 * Check if a role has at least the specified minimum role level.
 */
export function hasMinimumRole(userRole: UserRole, minRole: UserRole): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[minRole];
}

/**
 * Check if a user can manage another user based on role hierarchy.
 */
export function canManageRole(managerRole: UserRole, targetRole: UserRole): boolean {
  return ROLE_HIERARCHY[managerRole] > ROLE_HIERARCHY[targetRole];
}
