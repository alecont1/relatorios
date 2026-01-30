import { Navigate } from 'react-router-dom';
import { LoginForm, useAuthStore } from '@/features/auth';

/**
 * Login page.
 *
 * - Shows login form centered on page
 * - Redirects authenticated users to dashboard
 * - Mobile-friendly layout
 */
export function LoginPage() {
  const { isAuthenticated, isLoading } = useAuthStore();

  // Redirect if already authenticated
  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            SmartHand
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Entre com suas credenciais para acessar o sistema
          </p>
        </div>

        {/* Login card */}
        <div className="rounded-xl bg-white p-8 shadow-lg">
          <LoginForm />
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-gray-500">
          Nao tem acesso? Entre em contato com seu administrador.
        </p>
      </div>
    </div>
  );
}
