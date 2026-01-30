import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';
import { createUserSchema, type CreateUserFormData } from '@/features/auth';
import { PasswordInput } from '@/features/auth/components/PasswordInput';
import { useCreateUser } from '../api';

interface CreateUserFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CreateUserForm({ onSuccess, onCancel }: CreateUserFormProps) {
  const createUser = useCreateUser();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    reset,
  } = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      email: '',
      full_name: '',
      password: '',
      role: 'user',
    },
  });

  const onSubmit = async (data: CreateUserFormData) => {
    try {
      await createUser.mutateAsync(data);
      reset();
      onSuccess?.();
    } catch (error: unknown) {
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      setError('root', {
        message: axiosError.response?.data?.detail || 'Erro ao criar usuario',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Full Name */}
      <div>
        <label
          htmlFor="full_name"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Nome completo
        </label>
        <input
          {...register('full_name')}
          type="text"
          id="full_name"
          className={`
            block w-full rounded-lg border border-gray-300 px-4 py-3
            focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20
            ${errors.full_name ? 'border-red-500' : ''}
          `}
        />
        {errors.full_name && (
          <p className="mt-1 text-sm text-red-600">
            {errors.full_name.message}
          </p>
        )}
      </div>

      {/* Email */}
      <div>
        <label
          htmlFor="create_email"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Email
        </label>
        <input
          {...register('email')}
          type="email"
          id="create_email"
          className={`
            block w-full rounded-lg border border-gray-300 px-4 py-3
            focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20
            ${errors.email ? 'border-red-500' : ''}
          `}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">
            {errors.email.message}
          </p>
        )}
      </div>

      {/* Password */}
      <div>
        <PasswordInput
          {...register('password')}
          label="Senha"
          id="create_password"
          error={errors.password?.message}
        />
        <p className="mt-1 text-xs text-gray-500">
          Minimo 8 caracteres, com letra maiuscula, numero e caractere especial
        </p>
      </div>

      {/* Role */}
      <div>
        <label
          htmlFor="role"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Cargo
        </label>
        <select
          {...register('role')}
          id="role"
          className={`
            block w-full rounded-lg border border-gray-300 px-4 py-3
            focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20
            ${errors.role ? 'border-red-500' : ''}
          `}
        >
          <option value="user">Tecnico</option>
          <option value="manager">Gerente</option>
          <option value="admin">Administrador</option>
        </select>
        {errors.role && (
          <p className="mt-1 text-sm text-red-600">
            {errors.role.message}
          </p>
        )}
      </div>

      {/* Root error */}
      {errors.root && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {errors.root.message}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting || createUser.isPending}
          className="
            flex flex-1 items-center justify-center
            rounded-lg bg-blue-600 px-4 py-2 text-white
            hover:bg-blue-700 disabled:opacity-50
          "
        >
          {(isSubmitting || createUser.isPending) ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Criando...
            </>
          ) : (
            'Criar Usuario'
          )}
        </button>
      </div>
    </form>
  );
}
