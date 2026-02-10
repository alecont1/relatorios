import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search } from 'lucide-react'
import {
  useSuperAdminTenants,
  useSuspendTenant,
  useActivateTenant,
  useTenantPlans,
} from '@/features/superadmin/api'
import { TenantCard, SuspendTenantModal } from '@/features/superadmin/components'
import type { TenantStatus, TenantFilters, TenantWithConfig } from '@/features/superadmin/types'

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Todos os status' },
  { value: 'trial', label: 'Trial' },
  { value: 'active', label: 'Ativo' },
  { value: 'suspended', label: 'Suspenso' },
]

export function SuperAdminTenantsPage() {
  const navigate = useNavigate()

  const [filters, setFilters] = useState<TenantFilters>({
    page: 1,
    limit: 12,
  })
  const [searchInput, setSearchInput] = useState('')
  const [suspendTarget, setSuspendTarget] = useState<TenantWithConfig | null>(null)

  const { data, isLoading } = useSuperAdminTenants(filters)
  const { data: plans } = useTenantPlans()
  const suspendMutation = useSuspendTenant()
  const activateMutation = useActivateTenant()

  const handleStatusChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      status: value ? (value as TenantStatus) : undefined,
      page: 1,
    }))
  }

  const handlePlanChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      plan_id: value || undefined,
      page: 1,
    }))
  }

  const handleSearch = () => {
    setFilters((prev) => ({
      ...prev,
      search: searchInput.trim() || undefined,
      page: 1,
    }))
  }

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch()
  }

  const handleSuspend = (tenantId: string) => {
    const tenant = data?.items.find((t) => t.id === tenantId)
    if (tenant) setSuspendTarget(tenant)
  }

  const handleConfirmSuspend = (reason: string) => {
    if (!suspendTarget) return
    suspendMutation.mutate(
      { tenantId: suspendTarget.id, reason },
      { onSuccess: () => setSuspendTarget(null) }
    )
  }

  const handleActivate = (tenantId: string) => {
    activateMutation.mutate(tenantId)
  }

  const totalPages = data ? Math.ceil(data.total / (filters.limit ?? 12)) : 0
  const currentPage = filters.page ?? 1

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Gestao de Tenants</h1>
        <button
          onClick={() => navigate('/superadmin/tenants/new')}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Novo Tenant
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <select
          value={filters.status ?? ''}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {plans && plans.length > 0 && (
          <select
            value={filters.plan_id ?? ''}
            onChange={(e) => handlePlanChange(e.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Todos os planos</option>
            {plans.map((plan) => (
              <option key={plan.id} value={plan.id}>
                {plan.name}
              </option>
            ))}
          </select>
        )}

        <div className="flex items-center gap-1">
          <div className="relative">
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              placeholder="Buscar por nome ou slug..."
              className="w-64 rounded-lg border border-gray-300 pl-9 pr-3 py-2 text-sm"
            />
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          </div>
          <button
            onClick={handleSearch}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
          >
            Buscar
          </button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="h-48 animate-pulse rounded-xl border border-gray-200 bg-gray-100"
            />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((tenant) => (
              <TenantCard
                key={tenant.id}
                tenant={tenant}
                onSuspend={handleSuspend}
                onActivate={handleActivate}
                onClick={(id) => navigate(`/superadmin/tenants/${id}`)}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() =>
                  setFilters((prev) => ({ ...prev, page: currentPage - 1 }))
                }
                disabled={currentPage <= 1}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-sm text-gray-600">
                Pagina {currentPage} de {totalPages}
              </span>
              <button
                onClick={() =>
                  setFilters((prev) => ({ ...prev, page: currentPage + 1 }))
                }
                disabled={currentPage >= totalPages}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
              >
                Proxima
              </button>
            </div>
          )}

          <div className="mt-4 text-center text-sm text-gray-500">
            Total: {data.total} tenant(s)
          </div>
        </>
      ) : (
        <div className="rounded-xl border border-gray-200 bg-white py-12 text-center">
          <p className="text-gray-500">Nenhum tenant encontrado.</p>
        </div>
      )}

      {/* Suspend modal */}
      <SuspendTenantModal
        tenantName={suspendTarget?.name ?? ''}
        isOpen={!!suspendTarget}
        onConfirm={handleConfirmSuspend}
        onClose={() => setSuspendTarget(null)}
      />
    </div>
  )
}
