import { useState } from 'react';
import { Trash2, Loader2 } from 'lucide-react';
import { useUsers, useDeleteUser, ROLE_LABELS } from '../';
import type { User } from '@/features/auth';

interface UserListProps {
  onUserDeleted?: () => void;
}

export function UserList({ onUserDeleted }: UserListProps) {
  const { data, isLoading, error } = useUsers();
  const deleteUser = useDeleteUser();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (user: User) => {
    if (!confirm(`Tem certeza que deseja excluir ${user.full_name}?`)) {
      return;
    }

    setDeletingId(user.id);
    try {
      await deleteUser.mutateAsync(user.id);
      onUserDeleted?.();
    } catch (error: unknown) {
      const axiosError = error as {
        response?: { data?: { detail?: string } };
      };
      alert(axiosError.response?.data?.detail || 'Erro ao excluir usuario');
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-4 text-red-700">
        Erro ao carregar usuarios
      </div>
    );
  }

  if (!data?.users.length) {
    return (
      <div className="py-8 text-center text-gray-500">
        Nenhum usuario encontrado
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Nome
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Cargo
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
              Status
            </th>
            <th className="relative px-6 py-3">
              <span className="sr-only">Acoes</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {data.users.map((user) => (
            <tr key={user.id} className="hover:bg-gray-50">
              <td className="whitespace-nowrap px-6 py-4">
                <div className="font-medium text-gray-900">
                  {user.full_name}
                </div>
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-gray-500">
                {user.email}
              </td>
              <td className="whitespace-nowrap px-6 py-4">
                <span className="inline-flex rounded-full bg-blue-100 px-2 text-xs font-semibold leading-5 text-blue-800">
                  {ROLE_LABELS[user.role] || user.role}
                </span>
              </td>
              <td className="whitespace-nowrap px-6 py-4">
                <span
                  className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                    user.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {user.is_active ? 'Ativo' : 'Inativo'}
                </span>
              </td>
              <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                <button
                  onClick={() => handleDelete(user)}
                  disabled={deletingId === user.id}
                  className="text-red-600 hover:text-red-900 disabled:opacity-50"
                  title="Excluir usuario"
                >
                  {deletingId === user.id ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Trash2 className="h-5 w-5" />
                  )}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.total > data.users.length && (
        <div className="bg-gray-50 px-6 py-3 text-sm text-gray-500">
          Mostrando {data.users.length} de {data.total} usuarios
        </div>
      )}
    </div>
  );
}
