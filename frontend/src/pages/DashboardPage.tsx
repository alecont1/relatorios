import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ClipboardList,
  FileText,
  Award,
  Building2,
  Plus,
  ArrowRight,
  Clock,
  CheckCircle2,
  FileEdit,
  Archive,
  Loader2,
} from 'lucide-react'
import { useAuthStore } from '@/features/auth'
import { OnboardingBanner, useOnboardingGuard } from '@/features/onboarding'
import { reportApi } from '@/features/report/api/reportApi'
import { templateApi } from '@/features/template/api/templateApi'
import { certificateApi } from '@/features/certificate/api/certificateApi'

function StatCard({
  icon: Icon,
  label,
  value,
  color,
  isLoading,
}: {
  icon: React.ElementType
  label: string
  value: number | string
  color: string
  isLoading?: boolean
}) {
  const bgColors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
    gray: 'bg-gray-100 text-gray-600',
  }

  return (
    <div className="rounded-lg border bg-white p-4 flex items-center gap-4">
      <div className={`rounded-lg p-2.5 ${bgColors[color] ?? bgColors.gray}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0">
        <p className="text-sm text-gray-500 truncate">{label}</p>
        {isLoading ? (
          <Loader2 className="h-5 w-5 animate-spin text-gray-300 mt-0.5" />
        ) : (
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        )}
      </div>
    </div>
  )
}

function QuickAction({
  icon: Icon,
  label,
  description,
  to,
  color,
}: {
  icon: React.ElementType
  label: string
  description: string
  to: string
  color: string
}) {
  const bgColors: Record<string, string> = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    green: 'bg-green-600 hover:bg-green-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    amber: 'bg-amber-600 hover:bg-amber-700',
  }

  return (
    <Link
      to={to}
      className={`flex items-center gap-3 rounded-lg ${bgColors[color] ?? bgColors.blue} p-4 text-white transition-colors`}
    >
      <Icon className="h-5 w-5 shrink-0" />
      <div className="flex-1 min-w-0">
        <p className="font-medium">{label}</p>
        <p className="text-xs opacity-80">{description}</p>
      </div>
      <ArrowRight className="h-4 w-4 opacity-60 shrink-0" />
    </Link>
  )
}

export function DashboardPage() {
  const { user } = useAuthStore()
  useOnboardingGuard()

  const isTenantAdmin = user?.role === 'tenant_admin'
  const isSuperadmin = user?.role === 'superadmin'
  const canManage = isTenantAdmin || isSuperadmin

  // Fetch report counts by status (lightweight - limit: 0 just for totals)
  const { data: draftReports, isLoading: loadingDrafts } = useQuery({
    queryKey: ['dashboard', 'reports', 'draft'],
    queryFn: () => reportApi.list({ status: 'draft', limit: 0 }),
    staleTime: 60_000,
  })

  const { data: inProgressReports, isLoading: loadingInProgress } = useQuery({
    queryKey: ['dashboard', 'reports', 'in_progress'],
    queryFn: () => reportApi.list({ status: 'in_progress', limit: 0 }),
    staleTime: 60_000,
  })

  const { data: completedReports, isLoading: loadingCompleted } = useQuery({
    queryKey: ['dashboard', 'reports', 'completed'],
    queryFn: () => reportApi.list({ status: 'completed', limit: 0 }),
    staleTime: 60_000,
  })

  const { data: archivedReports, isLoading: loadingArchived } = useQuery({
    queryKey: ['dashboard', 'reports', 'archived'],
    queryFn: () => reportApi.list({ status: 'archived', limit: 0 }),
    staleTime: 60_000,
  })

  const { data: templates, isLoading: loadingTemplates } = useQuery({
    queryKey: ['dashboard', 'templates'],
    queryFn: () => templateApi.list({}),
    staleTime: 60_000,
    enabled: canManage,
  })

  const { data: certificates, isLoading: loadingCerts } = useQuery({
    queryKey: ['dashboard', 'certificates'],
    queryFn: () => certificateApi.list({ limit: 0 }),
    staleTime: 60_000,
    enabled: canManage,
  })

  const totalReports =
    (draftReports?.total ?? 0) +
    (inProgressReports?.total ?? 0) +
    (completedReports?.total ?? 0) +
    (archivedReports?.total ?? 0)

  const loadingReports = loadingDrafts || loadingInProgress || loadingCompleted || loadingArchived

  // Greeting based on time of day
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Bom dia' : hour < 18 ? 'Boa tarde' : 'Boa noite'

  return (
    <div className="space-y-6">
      <OnboardingBanner />

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {greeting}, {user?.full_name?.split(' ')[0]}!
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Aqui esta um resumo da sua conta SmartHand
        </p>
      </div>

      {/* Stats Cards */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Relatorios</h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={FileEdit}
            label="Rascunhos"
            value={draftReports?.total ?? 0}
            color="amber"
            isLoading={loadingDrafts}
          />
          <StatCard
            icon={Clock}
            label="Em Andamento"
            value={inProgressReports?.total ?? 0}
            color="blue"
            isLoading={loadingInProgress}
          />
          <StatCard
            icon={CheckCircle2}
            label="Concluidos"
            value={completedReports?.total ?? 0}
            color="green"
            isLoading={loadingCompleted}
          />
          <StatCard
            icon={Archive}
            label="Arquivados"
            value={archivedReports?.total ?? 0}
            color="gray"
            isLoading={loadingArchived}
          />
        </div>
      </div>

      {/* Admin Stats */}
      {canManage && (
        <div>
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Gestao</h2>
          <div className="grid gap-4 grid-cols-2 lg:grid-cols-3">
            <StatCard
              icon={ClipboardList}
              label="Total de Relatorios"
              value={totalReports}
              color="blue"
              isLoading={loadingReports}
            />
            <StatCard
              icon={FileText}
              label="Templates"
              value={templates?.total ?? 0}
              color="purple"
              isLoading={loadingTemplates}
            />
            <StatCard
              icon={Award}
              label="Certificados"
              value={certificates?.total ?? 0}
              color="green"
              isLoading={loadingCerts}
            />
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Acoes Rapidas</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <QuickAction
            icon={Plus}
            label="Novo Relatorio"
            description="Criar um relatorio a partir de um template"
            to="/reports"
            color="blue"
          />
          {canManage && (
            <QuickAction
              icon={FileText}
              label="Gerenciar Templates"
              description="Criar ou editar templates de relatorio"
              to="/templates"
              color="purple"
            />
          )}
          {canManage && (
            <QuickAction
              icon={Building2}
              label="Configurar Empresa"
              description="Logo, cores, marca d'agua e contato"
              to="/settings"
              color="green"
            />
          )}
        </div>
      </div>
    </div>
  )
}
