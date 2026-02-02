import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Plus,
  FileText,
  Clock,
  CheckCircle,
  Archive,
  Loader2,
  ChevronRight,
  Search,
} from 'lucide-react'
import { reportApi, type Report, type ReportStatus } from '@/features/report/api/reportApi'
import { templateApi } from '@/features/template/api/templateApi'
import { NewReportModal } from '@/features/report/components/NewReportModal'

const STATUS_CONFIG: Record<ReportStatus, { label: string; color: string; icon: typeof Clock }> = {
  draft: { label: 'Rascunho', color: 'bg-gray-500', icon: FileText },
  in_progress: { label: 'Em Andamento', color: 'bg-blue-500', icon: Clock },
  completed: { label: 'Concluido', color: 'bg-green-500', icon: CheckCircle },
  archived: { label: 'Arquivado', color: 'bg-purple-500', icon: Archive },
}

export function ReportsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [statusFilter, setStatusFilter] = useState<ReportStatus | ''>('')
  const [searchTerm, setSearchTerm] = useState('')

  // Fetch reports
  const { data, isLoading, error } = useQuery({
    queryKey: ['reports', statusFilter],
    queryFn: () =>
      reportApi.list({
        status: statusFilter || undefined,
        limit: 100,
      }),
  })

  // Fetch templates for modal
  const { data: templatesData } = useQuery({
    queryKey: ['templates', 'active'],
    queryFn: () => templateApi.list({ status: 'active' }),
  })

  // Create report mutation
  const createMutation = useMutation({
    mutationFn: reportApi.create,
    onSuccess: (newReport) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setIsModalOpen(false)
      // Navigate to fill the new report
      navigate(`/reports/${newReport.id}`)
    },
  })

  // Filter reports by search term
  const filteredReports = data?.reports.filter((report) =>
    report.title.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erro ao carregar relatorios</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Relatorios</h1>
          <p className="text-sm text-gray-500">
            {data?.total || 0} relatorio(s) encontrado(s)
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Novo Relatorio
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por titulo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ReportStatus | '')}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Todos os Status</option>
          <option value="draft">Rascunho</option>
          <option value="in_progress">Em Andamento</option>
          <option value="completed">Concluido</option>
          <option value="archived">Arquivado</option>
        </select>
      </div>

      {/* Reports List */}
      {filteredReports.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum relatorio encontrado</p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="mt-4 text-blue-600 hover:underline"
          >
            Criar primeiro relatorio
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredReports.map((report) => (
            <ReportCard
              key={report.id}
              report={report}
              onClick={() => navigate(`/reports/${report.id}`)}
              formatDate={formatDate}
            />
          ))}
        </div>
      )}

      {/* New Report Modal */}
      <NewReportModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={(data) => createMutation.mutate(data)}
        templates={templatesData?.templates || []}
        isSubmitting={createMutation.isPending}
        error={createMutation.error?.message}
      />
    </div>
  )
}

interface ReportCardProps {
  report: Report
  onClick: () => void
  formatDate: (date: string) => string
}

function ReportCard({ report, onClick, formatDate }: ReportCardProps) {
  const statusConfig = STATUS_CONFIG[report.status]
  const StatusIcon = statusConfig.icon

  return (
    <div
      onClick={onClick}
      className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md hover:border-gray-300 cursor-pointer transition-all"
    >
      <div className="flex items-center gap-4">
        {/* Status Badge */}
        <div
          className={`flex items-center justify-center w-10 h-10 rounded-full ${statusConfig.color} bg-opacity-20`}
        >
          <StatusIcon className={`h-5 w-5 ${statusConfig.color.replace('bg-', 'text-')}`} />
        </div>

        {/* Info */}
        <div>
          <h3 className="font-medium text-gray-900">{report.title}</h3>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            {report.template_name && (
              <span className="bg-gray-100 px-2 py-0.5 rounded">
                {report.template_name}
              </span>
            )}
            <span>Criado em {formatDate(report.created_at)}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Status Label */}
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${statusConfig.color} text-white`}
        >
          {statusConfig.label}
        </span>

        {/* Arrow */}
        <ChevronRight className="h-5 w-5 text-gray-400" />
      </div>
    </div>
  )
}
