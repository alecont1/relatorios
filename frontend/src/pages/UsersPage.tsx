import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { UserList, CreateUserModal } from '@/features/admin';

/**
 * User management page.
 *
 * Only accessible to admin and superadmin roles.
 * Allows viewing, creating, and deleting users.
 */
export function UsersPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="p-6 sm:p-8">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Usuarios
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Gerencie os usuarios do sistema
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="
            inline-flex items-center rounded-lg
            bg-blue-600 px-4 py-2 text-white
            hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
          "
        >
          <UserPlus className="mr-2 h-5 w-5" />
          Novo Usuario
        </button>
      </div>

      {/* Content */}
      <UserList />

      {/* Create User Modal */}
      <CreateUserModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}
