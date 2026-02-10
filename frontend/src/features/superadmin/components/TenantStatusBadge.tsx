import type { TenantStatus } from '../types'

const STATUS_STYLES: Record<TenantStatus, string> = {
  trial: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  suspended: 'bg-red-100 text-red-800',
}

const STATUS_LABELS: Record<TenantStatus, string> = {
  trial: 'Trial',
  active: 'Ativo',
  suspended: 'Suspenso',
}

function getDaysRemaining(trialEndsAt: string): number {
  const now = new Date()
  const end = new Date(trialEndsAt)
  const diff = end.getTime() - now.getTime()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

interface TenantStatusBadgeProps {
  status: TenantStatus
  trialEndsAt?: string | null
}

export function TenantStatusBadge({ status, trialEndsAt }: TenantStatusBadgeProps) {
  const daysRemaining = status === 'trial' && trialEndsAt
    ? getDaysRemaining(trialEndsAt)
    : null

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
      {daysRemaining !== null && (
        <span className="text-[10px] font-normal">
          ({daysRemaining}d restantes)
        </span>
      )}
    </span>
  )
}
