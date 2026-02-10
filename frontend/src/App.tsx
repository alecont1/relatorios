import { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { DashboardPage, LoginPage, UnauthorizedPage, UsersPage, TenantsPage, TenantSettingsPage, TemplatesPage, TemplateConfigPage, ReportsPage, ReportFillPage, CertificatesPage, OnboardingPage, SuperAdminTenantsPage, CreateTenantWizard, SuperAdminTenantDetailsPage, SuperAdminPlansPage } from '@/pages';
import {
  ProtectedRoute,
  useRefreshToken,
  useAuthStore,
} from '@/features/auth';
import { useTheme, useBrandingLoader } from '@/features/tenant';
import { AppLayout } from '@/components/layout';
import { OfflineIndicator } from '@/components/ui';

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

function App() {
  useTheme();  // Apply tenant branding via CSS variables
  useBrandingLoader();  // Load tenant branding data

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <OfflineIndicator />
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
                <ProtectedRoute allowedRoles={['tenant_admin', 'superadmin']}>
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
                <ProtectedRoute allowedRoles={['tenant_admin', 'superadmin']}>
                  <AppLayout>
                    <TenantSettingsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/templates"
              element={
                <ProtectedRoute allowedRoles={['tenant_admin', 'superadmin']}>
                  <AppLayout>
                    <TemplatesPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/templates/:templateId/configure"
              element={
                <ProtectedRoute allowedRoles={['tenant_admin', 'superadmin']}>
                  <AppLayout>
                    <TemplateConfigPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/certificates"
              element={
                <ProtectedRoute allowedRoles={['tenant_admin', 'superadmin']}>
                  <AppLayout>
                    <CertificatesPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ReportsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports/:reportId"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ReportFillPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Onboarding wizard (full-screen, no AppLayout) */}
            <Route
              path="/onboarding"
              element={
                <ProtectedRoute allowedRoles={['tenant_admin']}>
                  <OnboardingPage />
                </ProtectedRoute>
              }
            />

            {/* SuperAdmin routes */}
            <Route
              path="/superadmin/tenants"
              element={
                <ProtectedRoute allowedRoles={['superadmin']}>
                  <AppLayout>
                    <SuperAdminTenantsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/superadmin/tenants/new"
              element={
                <ProtectedRoute allowedRoles={['superadmin']}>
                  <AppLayout>
                    <CreateTenantWizard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/superadmin/tenants/:tenantId"
              element={
                <ProtectedRoute allowedRoles={['superadmin']}>
                  <AppLayout>
                    <SuperAdminTenantDetailsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/superadmin/plans"
              element={
                <ProtectedRoute allowedRoles={['superadmin']}>
                  <AppLayout>
                    <SuperAdminPlansPage />
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
