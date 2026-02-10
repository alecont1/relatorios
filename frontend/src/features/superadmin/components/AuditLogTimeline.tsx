import {
  Plus,
  Pencil,
  Pause,
  Play,
  ArrowRightLeft,
  History,
} from 'lucide-react'
import type { TenantAuditLog } from '../types'

const ACTION_CONFIG: Record<string, { icon: typeof Plus; color: string; label: string }> = {
  created: { icon: Plus, color: 'text-green-500 bg-green-50', label: 'Criado' },
  updated: { icon: Pencil, color: 'text-blue-500 bg-blue-50', label: 'Atualizado' },
  suspended: { icon: Pause, color: 'text-red-500 bg-red-50', label: 'Suspenso' },
  activated: { icon: Play, color: 'text-green-500 bg-green-50', label: 'Ativado' },
  plan_changed: { icon: ArrowRightLeft, color: 'text-purple-500 bg-purple-50', label: 'Plano alterado' },
}

const DEFAULT_ACTION = { icon: History, color: 'text-gray-500 bg-gray-50', label: '' }

function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

interface AuditLogTimelineProps {
  logs: TenantAuditLog[]
}

export function AuditLogTimeline({ logs }: AuditLogTimelineProps) {
  if (logs.length === 0) {
    return (
      <p className="text-sm text-gray-500">Nenhum registro de auditoria encontrado.</p>
    )
  }

  return (
    <div className="relative space-y-0">
      {logs.map((log, index) => {
        const config = ACTION_CONFIG[log.action] ?? DEFAULT_ACTION
        const Icon = config.icon
        const isLast = index === logs.length - 1

        return (
          <div key={log.id} className="relative flex gap-4 pb-6">
            {!isLast && (
              <div className="absolute left-[17px] top-10 h-[calc(100%-24px)] w-px bg-gray-200" />
            )}

            <div
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${config.color}`}
            >
              <Icon className="h-4 w-4" />
            </div>

            <div className="min-w-0 flex-1 pt-1">
              <p className="text-sm font-medium text-gray-900">
                {config.label || log.action}
              </p>
              {log.reason && (
                <p className="mt-0.5 text-xs text-gray-600">
                  Motivo: {log.reason}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-400">
                {formatDate(log.created_at)}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
