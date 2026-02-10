import { useState } from 'react'
import { Users } from 'lucide-react'
import { CreateUserForm } from '@/features/admin/components/CreateUserForm'
import { useUsers } from '@/features/admin/api'

interface UsersStepProps {
  onComplete: () => void
}

export function UsersStep({ onComplete }: UsersStepProps) {
  const { data: usersData } = useUsers()
  const [createdCount, setCreatedCount] = useState(0)

  const users = usersData?.users || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Equipe</h2>
        <p className="mt-1 text-sm text-gray-500">
          Convide membros da equipe para colaborar nos relatorios
        </p>
      </div>

      {/* Existing users list */}
      {users.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">
            Usuarios cadastrados ({users.length})
          </h3>
          <div className="divide-y rounded-lg border">
            {users.map((user) => (
              <div key={user.id} className="flex items-center gap-3 p-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-700">
                  {user.full_name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {user.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create user form */}
      <div className="onboarding-users-form">
        <h3 className="mb-3 text-sm font-medium text-gray-700">
          <Users className="mr-1 inline h-4 w-4" />
          Adicionar novo membro
        </h3>
        <div className="rounded-lg border p-4">
          <CreateUserForm
            onSuccess={() => setCreatedCount((c) => c + 1)}
          />
        </div>
      </div>

      {createdCount > 0 && (
        <p className="text-sm text-green-600">
          {createdCount} usuario(s) criado(s) nesta sessao
        </p>
      )}

      <div className="flex justify-start">
        <button
          onClick={onComplete}
          className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
        >
          Concluir Passo
        </button>
      </div>
    </div>
  )
}
