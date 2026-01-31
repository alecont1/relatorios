import { useState } from 'react'
import { Building2, ToggleLeft, ToggleRight } from 'lucide-react'
import { useTenants, useUpdateTenant } from '../api'
import type { Tenant } from '../types'

export function TenantList() {
  const [showInactive, setShowInactive] = useState(false)
  const { data, isLoading, error } = useTenants(showInactive)
  const updateTenant = useUpdateTenant()

  const handleToggleActive = (tenant: Tenant) => {
    updateTenant.mutate({
      id: tenant.id,
      is_active: !tenant.is_active,
    })
  }

  if (isLoading) {
    return <div className="text-gray-500">Carregando tenants...</div>
  }

  if (error) {
    return <div className="text-red-500">Erro ao carregar tenants</div>
  }

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <label className="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="rounded border-gray-300"
          />
          Mostrar inativos
        </label>
      </div>

      <div className="overflow-hidden rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Tenant
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Slug
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Acoes
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {data?.tenants.map((tenant) => (
              <tr key={tenant.id}>
                <td className="whitespace-nowrap px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Building2 className="h-5 w-5 text-gray-400" />
                    <span className="font-medium text-gray-900">{tenant.name}</span>
                  </div>
                </td>
                <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                  {tenant.slug}
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <span
                    className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                      tenant.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {tenant.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="whitespace-nowrap px-6 py-4">
                  <button
                    onClick={() => handleToggleActive(tenant)}
                    disabled={updateTenant.isPending}
                    className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
                  >
                    {tenant.is_active ? (
                      <>
                        <ToggleRight className="h-4 w-4" />
                        Desativar
                      </>
                    ) : (
                      <>
                        <ToggleLeft className="h-4 w-4" />
                        Ativar
                      </>
                    )}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Total: {data?.total ?? 0} tenant(s)
      </div>
    </div>
  )
}
