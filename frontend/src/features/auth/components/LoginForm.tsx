import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useLogin } from '../api';
import { loginSchema, type LoginFormData } from '../schemas';
import { PasswordInput } from './PasswordInput';

/**
 * Login form component.
 *
 * Features:
 * - React Hook Form with Zod validation
 * - Shows specific backend error messages
 * - Redirects to intended page after login
 * - Loading state during submission
 */
export function LoginForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const login = useLogin();

  // Get redirect destination from location state
  const from = (location.state as { from?: Location })?.from?.pathname || '/';

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login.mutateAsync(data);
      // Redirect to intended destination
      navigate(from, { replace: true });
    } catch (error: unknown) {
      // Extract error message from response
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      const message =
        axiosError.response?.data?.detail || 'Erro ao fazer login';

      // Show error in form
      setError('root', { message });
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6"
      noValidate
    >
      {/* Email field */}
      <div>
        <label
          htmlFor="email"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Email
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          autoComplete="email"
          placeholder="seu@email.com"
          className={`
            block w-full rounded-lg border border-gray-300 px-4 py-3
            text-base placeholder-gray-400
            focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20
            ${errors.email ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''}
          `}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p
            id="email-error"
            className="mt-1 text-sm text-red-600"
            role="alert"
          >
            {errors.email.message}
          </p>
        )}
      </div>

      {/* Password field */}
      <PasswordInput
        {...register('password')}
        label="Senha"
        id="password"
        autoComplete="current-password"
        placeholder="Digite sua senha"
        error={errors.password?.message}
      />

      {/* Root error (backend errors) */}
      {errors.root && (
        <div
          className="rounded-lg bg-red-50 p-4 text-sm text-red-700"
          role="alert"
        >
          {errors.root.message}
        </div>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={isSubmitting || login.isPending}
        className="
          flex w-full items-center justify-center
          rounded-lg bg-blue-600 px-4 py-3
          text-base font-medium text-white
          hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
          disabled:cursor-not-allowed disabled:opacity-50
          transition-colors
        "
      >
        {(isSubmitting || login.isPending) ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Entrando...
          </>
        ) : (
          'Entrar'
        )}
      </button>
    </form>
  );
}
