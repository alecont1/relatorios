import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { GitBranch, Clock, CheckCircle, FileText, Archive, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { reportApi, type RevisionEntry, type ReportStatus } from '../api/reportApi'

const STATUS_LABELS: Record<ReportStatus, { label: string; icon: typeof Clock; color: string }> = {
  draft: { label: 'Rascunho', icon: FileText, color: 'text-gray-500' },
  in_progress: { label: 'Em Andamento', icon: Clock, color: 'text-blue-500' },
  completed: { label: 'Concluido', icon: CheckCircle, color: 'text-green-500' },
  archived: { label: 'Arquivado', icon: Archive, color: 'text-purple-500' },
}

interface RevisionHistoryProps {
  reportId: string
  currentReportId: string
  revisionNumber: number
}

export function RevisionHistory({ reportId, currentReportId, revisionNumber }: RevisionHistoryProps) {
  const navigate = useNavigate()
  const [isExpanded, setIsExpanded] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['revisions', reportId],
    queryFn: () => reportApi.listRevisions(reportId),
    enabled: isExpanded,
    staleTime: 30_000,
  })

  // Only show if there's revision context (revision_number > 0 or we know there are revisions)
  if (revisionNumber === 0 && !data?.revisions?.length) {
    // Show collapsed button that might reveal revisions on click
  }

  return (
    <div className="bg-white rounded-lg border">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
      >
        <div className="flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">
            Historico de Revisoes
          </span>
          {revisionNumber > 0 && (
            <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
              Rev. {revisionNumber}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="border-t px-4 pb-4">
          {isLoading ? (
            <p className="text-sm text-gray-400 py-3">Carregando...</p>
          ) : data && data.revisions.length > 0 ? (
            <div className="space-y-2 mt-3">
              {data.revisions.map((rev: RevisionEntry) => {
                const statusInfo = STATUS_LABELS[rev.status] || STATUS_LABELS.draft
                const StatusIcon = statusInfo.icon
                const isCurrent = rev.id === currentReportId

                return (
                  <button
                    key={rev.id}
                    onClick={() => {
                      if (!isCurrent) navigate(`/reports/${rev.id}`)
                    }}
                    disabled={isCurrent}
                    className={`w-full flex items-center justify-between p-3 rounded-lg text-left transition-colors ${
                      isCurrent
                        ? 'bg-blue-50 border border-blue-200 cursor-default'
                        : 'bg-gray-50 hover:bg-gray-100 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <StatusIcon className={`h-4 w-4 ${statusInfo.color}`} />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {rev.revision_number === 0 ? 'Original' : `Revisao ${rev.revision_number}`}
                          {isCurrent && (
                            <span className="ml-2 text-xs text-blue-600">(atual)</span>
                          )}
                        </p>
                        {rev.revision_notes && (
                          <p className="text-xs text-gray-500 mt-0.5">
                            {rev.revision_notes}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">
                        {new Date(rev.created_at).toLocaleDateString('pt-BR')}
                      </p>
                      <p className={`text-xs ${statusInfo.color}`}>
                        {statusInfo.label}
                      </p>
                    </div>
                  </button>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-3">
              Nenhuma revisao encontrada.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
