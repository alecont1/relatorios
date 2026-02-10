import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Rocket, X, ArrowRight } from 'lucide-react'
import { useOnboardingStatus } from '../api'
import { useAuthStore } from '@/features/auth'

export function OnboardingBanner() {
  const { user } = useAuthStore()
  const [dismissed, setDismissed] = useState(false)

  const isTenantAdmin = user?.role === 'tenant_admin'
  const { data: status, isLoading } = useOnboardingStatus(isTenantAdmin)

  if (dismissed || isLoading || !status || status.is_completed || !isTenantAdmin) {
    return null
  }

  const completedCount = status.steps.filter(
    (s) => s.status === 'completed' || s.status === 'skipped'
  ).length

  return (
    <div className="relative rounded-lg border border-blue-200 bg-blue-50 p-4">
      <button
        onClick={() => setDismissed(true)}
        className="absolute right-2 top-2 p-1 text-blue-400 hover:text-blue-600"
      >
        <X className="h-4 w-4" />
      </button>
      <div className="flex items-center gap-3">
        <Rocket className="h-6 w-6 text-blue-600" />
        <div className="flex-1">
          <p className="font-medium text-blue-900">
            {completedCount} de 5 passos concluidos
          </p>
          <p className="text-sm text-blue-700">
            Continue a configuracao inicial para aproveitar ao maximo a plataforma.
          </p>
        </div>
        <Link
          to="/onboarding"
          className="flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Continuar configuracao
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  )
}
