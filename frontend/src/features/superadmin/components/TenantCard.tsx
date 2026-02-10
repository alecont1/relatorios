import { Building2, Pause, Play } from 'lucide-react'
import type { TenantWithConfig } from '../types'
import { TenantStatusBadge } from './TenantStatusBadge'
import { TenantUsageBar } from './TenantUsageBar'

interface TenantCardProps {
  tenant: TenantWithConfig
  onSuspend?: (tenantId: string) => void
  onActivate?: (tenantId: string) => void
  onClick?: (tenantId: string) => void
}

export function TenantCard({ tenant, onSuspend, onActivate, onClick }: TenantCardProps) {
  const { config, usage } = tenant

  return (
    <div
      className={`rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={() => onClick?.(tenant.id)}
    >
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
            <Building2 className="h-5 w-5 text-gray-500" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900">{tenant.name}</h3>
            <p className="text-xs text-gray-500">{tenant.slug}</p>
          </div>
        </div>
        <TenantStatusBadge
          status={config.status}
          trialEndsAt={config.trial_ends_at}
        />
      </div>

      {config.plan && (
        <p className="mb-3 text-xs text-gray-500">
          Plano: <span className="font-medium text-gray-700">{config.plan.name}</span>
        </p>
      )}

      {usage && (
        <div className="mb-4 space-y-2">
          <TenantUsageBar
            label="Usuarios"
            used={usage.users_count}
            max={config.limits.max_users}
          />
          <TenantUsageBar
            label="Armazenamento"
            used={usage.storage_used_gb}
            max={config.limits.max_storage_gb}
            unit="GB"
          />
          <TenantUsageBar
            label="Relatorios/Mes"
            used={usage.reports_this_month}
            max={config.limits.max_reports_month}
          />
        </div>
      )}

      {(onSuspend || onActivate) && (
        <div className="flex gap-2 border-t border-gray-100 pt-3">
          {config.status !== 'suspended' && onSuspend && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onSuspend(tenant.id)
              }}
              className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50"
            >
              <Pause className="h-3.5 w-3.5" />
              Suspender
            </button>
          )}
          {config.status === 'suspended' && onActivate && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onActivate(tenant.id)
              }}
              className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-medium text-green-600 hover:bg-green-50"
            >
              <Play className="h-3.5 w-3.5" />
              Ativar
            </button>
          )}
        </div>
      )}
    </div>
  )
}
