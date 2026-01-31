import { useState } from 'react'
import { Plus } from 'lucide-react'
import { TenantList, CreateTenantModal } from '@/features/tenant/components'

export function TenantsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tenants</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Novo Tenant
        </button>
      </div>

      <TenantList />

      <CreateTenantModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  )
}
