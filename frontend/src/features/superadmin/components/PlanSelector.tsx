import { Check } from 'lucide-react'
import type { TenantPlan } from '../types'

interface PlanSelectorProps {
  plans: TenantPlan[]
  selectedPlanId?: string | null
  onChange: (planId: string) => void
  showDetails?: boolean
}

export function PlanSelector({
  plans,
  selectedPlanId,
  onChange,
  showDetails = true,
}: PlanSelectorProps) {
  const activePlans = plans.filter((p) => p.is_active)

  if (activePlans.length === 0) {
    return (
      <p className="text-sm text-gray-500">Nenhum plano disponivel.</p>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {activePlans.map((plan) => {
        const isSelected = plan.id === selectedPlanId

        return (
          <button
            key={plan.id}
            type="button"
            onClick={() => onChange(plan.id)}
            className={`relative rounded-xl border-2 p-4 text-left transition-all ${
              isSelected
                ? 'border-blue-600 bg-blue-50 ring-1 ring-blue-600'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            {isSelected && (
              <div className="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600">
                <Check className="h-3 w-3 text-white" />
              </div>
            )}

            <h3 className="text-base font-semibold text-gray-900">{plan.name}</h3>

            {plan.price_display && (
              <p className="mt-1 text-sm font-medium text-blue-600">{plan.price_display}</p>
            )}

            {plan.description && (
              <p className="mt-1 text-xs text-gray-500">{plan.description}</p>
            )}

            {showDetails && (
              <div className="mt-3 space-y-1 border-t border-gray-100 pt-3">
                <p className="text-xs text-gray-600">
                  {plan.limits.max_users} usuarios
                </p>
                <p className="text-xs text-gray-600">
                  {plan.limits.max_storage_gb} GB armazenamento
                </p>
                <p className="text-xs text-gray-600">
                  {plan.limits.max_reports_month} relatorios/mes
                </p>

                <div className="mt-2 flex flex-wrap gap-1">
                  {plan.features.export_excel && (
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">Excel</span>
                  )}
                  {plan.features.watermark && (
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">Watermark</span>
                  )}
                  {plan.features.custom_pdf && (
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">PDF Custom</span>
                  )}
                  {plan.features.gps_required && (
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">GPS</span>
                  )}
                  {plan.features.certificate_required && (
                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600">Certificado</span>
                  )}
                </div>
              </div>
            )}
          </button>
        )
      })}
    </div>
  )
}
