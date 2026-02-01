import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { LogOut, Users, Home, Building2, Settings, FileText } from 'lucide-react';
import { queryClient } from '@/lib/queryClient';
import { LoginPage, UnauthorizedPage, UsersPage, TenantsPage, TenantSettingsPage, TemplatesPage } from '@/pages';
import {
  ProtectedRoute,
  useRefreshToken,
  useAuthStore,
  useLogout,
} from '@/features/auth';
import { useTheme } from '@/features/tenant';

/**
 * Auth initializer component.
 *
 * Attempts to recover session via refresh token on app load.
 * This runs once when the app mounts if user was previously authenticated.
 */
function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, accessToken, isLoading } = useAuthStore();
  const refresh = useRefreshToken();

  useEffect(() => {
    // If we have persisted auth but no token, try to refresh
    if (isAuthenticated && !accessToken && isLoading) {
      refresh.mutate();
    } else if (!isAuthenticated && isLoading) {
      // No persisted auth, just clear loading
      useAuthStore.getState().setLoading(false);
    }
  }, [isAuthenticated, accessToken, isLoading, refresh]);

  return <>{children}</>;
}

/**
 * App layout with navigation.
 */
function AppLayout({ children }: { children: React.ReactNode }) {
  const { user } = useAuthStore();
  const logout = useLogout();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout.mutateAsync();
    navigate('/login');
  };

  const canManageUsers = user?.role === 'admin' || user?.role === 'superadmin';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-xl font-bold text-gray-900">
                SmartHand
              </Link>
              <div className="flex gap-4">
                <Link
                  to="/"
                  className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                >
                  <Home className="h-4 w-4" />
                  Dashboard
                </Link>
                {canManageUsers && (
                  <Link
                    to="/users"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Users className="h-4 w-4" />
                    Usuarios
                  </Link>
                )}
                {canManageUsers && (
                  <Link
                    to="/templates"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <FileText className="h-4 w-4" />
                    Templates
                  </Link>
                )}
                {user?.role === 'superadmin' && (
                  <Link
                    to="/tenants"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Building2 className="h-4 w-4" />
                    Tenants
                  </Link>
                )}
                {(user?.role === 'admin' || user?.role === 'superadmin') && (
                  <Link
                    to="/settings"
                    className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
                  >
                    <Settings className="h-4 w-4" />
                    Configuracoes
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {user?.full_name}
              </span>
              <button
                onClick={handleLogout}
                disabled={logout.isPending}
                className="
                  flex items-center gap-1 rounded-lg
                  px-3 py-2 text-sm text-gray-600
                  hover:bg-gray-100 hover:text-gray-900
                "
              >
                <LogOut className="h-4 w-4" />
                Sair
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Page content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}

/**
 * Dashboard page.
 */
function DashboardPage() {
  const { user } = useAuthStore();
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p className="mt-2 text-gray-600">
        Bem-vindo, {user?.full_name}!
      </p>
      <p className="text-sm text-gray-500">
        Cargo: {user?.role}
      </p>
    </div>
  );
}

function App() {
  useTheme();  // Apply tenant branding via CSS variables

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthInitializer>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
                  <AppLayout>
                    <UsersPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tenants"
              element={
                <ProtectedRoute allowedRoles={['superadmin']}>
                  <AppLayout>
                    <TenantsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
                  <AppLayout>
                    <TenantSettingsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/templates"
              element={
                <ProtectedRoute allowedRoles={['admin', 'superadmin']}>
                  <AppLayout>
                    <TemplatesPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Catch-all redirect to login */}
            <Route path="*" element={<LoginPage />} />
          </Routes>
        </AuthInitializer>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
