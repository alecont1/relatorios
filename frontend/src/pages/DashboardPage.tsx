import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
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
  Camera,
  AlertTriangle,
  Users,
} from 'lucide-react'
import { useAuthStore } from '@/features/auth'
import { OnboardingBanner, useOnboardingGuard } from '@/features/onboarding'
import { api } from '@/lib/axios'

// --- Types ---

interface StatusCount {
  status: string
  count: number
}

interface MonthCount {
  month: string
  count: number
}

interface TemplateCount {
  template_name: string
  count: number
}

interface UserCount {
  user_id: string
  user_name: string
  count: number
}

interface CertificateStats {
  total: number
  expiring_in_30_days: number
  expired: number
}

interface DashboardMetrics {
  reports_by_status: StatusCount[]
  reports_by_month: MonthCount[]
  reports_by_template: TemplateCount[]
  reports_by_user: UserCount[]
  reports_by_project: Array<{ project_id: string; project_name: string; count: number }>
  avg_completion_hours: number | null
  total_reports: number
  total_photos: number
  certificate_stats: CertificateStats
}

// --- API ---

async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const response = await api.get('/dashboard/metrics')
  return response.data
}

// --- Helpers ---

const STATUS_LABELS: Record<string, string> = {
  draft: 'Rascunhos',
  in_progress: 'Em Andamento',
  completed: 'Concluidos',
  archived: 'Arquivados',
}

const STATUS_COLORS: Record<string, string> = {
  draft: '#f59e0b',
  in_progress: '#3b82f6',
  completed: '#22c55e',
  archived: '#a855f7',
}

const MONTH_LABELS: Record<string, string> = {
  '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
  '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
  '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez',
}

function formatMonth(ym: string): string {
  const parts = ym.split('-')
  if (parts.length === 2) {
    return MONTH_LABELS[parts[1]] || parts[1]
  }
  return ym
}

function formatHours(hours: number | null): string {
  if (hours === null) return '--'
  if (hours < 1) return `${Math.round(hours * 60)} min`
  if (hours < 24) return `${hours}h`
  return `${Math.round(hours / 24)}d`
}

// --- Components ---

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
    red: 'bg-red-50 text-red-600',
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

// --- Main Page ---

export function DashboardPage() {
  const { user } = useAuthStore()
  useOnboardingGuard()

  const isTenantAdmin = user?.role === 'tenant_admin'
  const isSuperadmin = user?.role === 'superadmin'
  const canManage = isTenantAdmin || isSuperadmin

  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard', 'metrics'],
    queryFn: fetchDashboardMetrics,
    staleTime: 60_000,
  })

  // Build status counts map for quick access
  const statusMap: Record<string, number> = {}
  metrics?.reports_by_status.forEach((s) => {
    statusMap[s.status] = s.count
  })

  // Build pie chart data
  const pieData = metrics?.reports_by_status
    .filter((s) => s.count > 0)
    .map((s) => ({
      name: STATUS_LABELS[s.status] || s.status,
      value: s.count,
      color: STATUS_COLORS[s.status] || '#94a3b8',
    })) || []

  // Build bar chart data
  const barData = metrics?.reports_by_month.map((m) => ({
    month: formatMonth(m.month),
    count: m.count,
  })) || []

  // Greeting based on time of day
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Bom dia' : hour < 18 ? 'Boa tarde' : 'Boa noite'

  const certStats = metrics?.certificate_stats
  const hasExpiringCerts = (certStats?.expiring_in_30_days ?? 0) > 0 || (certStats?.expired ?? 0) > 0

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

      {/* Certificate Expiry Alert */}
      {canManage && hasExpiringCerts && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">
              Atencao: Certificados de calibracao
            </p>
            <p className="text-sm text-amber-700 mt-1">
              {certStats?.expired ? `${certStats.expired} vencido(s)` : ''}
              {certStats?.expired && certStats?.expiring_in_30_days ? ' e ' : ''}
              {certStats?.expiring_in_30_days ? `${certStats.expiring_in_30_days} vencendo nos proximos 30 dias` : ''}
            </p>
            <Link
              to="/certificates"
              className="text-sm text-amber-800 underline hover:text-amber-900 mt-1 inline-block"
            >
              Ver certificados
            </Link>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Resumo</h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={ClipboardList}
            label="Total de Relatorios"
            value={metrics?.total_reports ?? 0}
            color="blue"
            isLoading={isLoading}
          />
          <StatCard
            icon={Camera}
            label="Total de Fotos"
            value={metrics?.total_photos ?? 0}
            color="purple"
            isLoading={isLoading}
          />
          <StatCard
            icon={Clock}
            label="Tempo Medio"
            value={formatHours(metrics?.avg_completion_hours ?? null)}
            color="amber"
            isLoading={isLoading}
          />
          <StatCard
            icon={Award}
            label="Certificados"
            value={certStats?.total ?? 0}
            color="green"
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Status Cards */}
      <div>
        <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">Relatorios por Status</h2>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={FileEdit}
            label="Rascunhos"
            value={statusMap['draft'] ?? 0}
            color="amber"
            isLoading={isLoading}
          />
          <StatCard
            icon={Clock}
            label="Em Andamento"
            value={statusMap['in_progress'] ?? 0}
            color="blue"
            isLoading={isLoading}
          />
          <StatCard
            icon={CheckCircle2}
            label="Concluidos"
            value={statusMap['completed'] ?? 0}
            color="green"
            isLoading={isLoading}
          />
          <StatCard
            icon={Archive}
            label="Arquivados"
            value={statusMap['archived'] ?? 0}
            color="gray"
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Charts */}
      {canManage && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Bar Chart - Reports by Month */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-4">
              Relatorios por Mes (ultimos 12 meses)
            </h3>
            {isLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="h-6 w-6 animate-spin text-gray-300" />
              </div>
            ) : barData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" name="Relatorios" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 text-center py-12">
                Nenhum dado disponivel
              </p>
            )}
          </div>

          {/* Pie Chart - Reports by Status */}
          <div className="bg-white rounded-lg border p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-4">
              Distribuicao por Status
            </h3>
            {isLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="h-6 w-6 animate-spin text-gray-300" />
              </div>
            ) : pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 text-center py-12">
                Nenhum dado disponivel
              </p>
            )}
          </div>
        </div>
      )}

      {/* Tables */}
      {canManage && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Top Technicians */}
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-gray-400" />
                <h3 className="text-sm font-medium text-gray-700">
                  Top Tecnicos
                </h3>
              </div>
            </div>
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <Loader2 className="h-5 w-5 animate-spin text-gray-300" />
              </div>
            ) : metrics?.reports_by_user && metrics.reports_by_user.length > 0 ? (
              <div className="divide-y">
                {metrics.reports_by_user.map((u, i) => (
                  <div
                    key={u.user_id}
                    className="flex items-center justify-between px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium text-gray-400 w-5">
                        {i + 1}.
                      </span>
                      <span className="text-sm text-gray-900">{u.user_name}</span>
                    </div>
                    <span className="text-sm font-medium text-blue-600">
                      {u.count} relatorio{u.count !== 1 ? 's' : ''}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-8">
                Nenhum dado disponivel
              </p>
            )}
          </div>

          {/* Top Templates */}
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-gray-400" />
                <h3 className="text-sm font-medium text-gray-700">
                  Top Templates
                </h3>
              </div>
            </div>
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <Loader2 className="h-5 w-5 animate-spin text-gray-300" />
              </div>
            ) : metrics?.reports_by_template && metrics.reports_by_template.length > 0 ? (
              <div className="divide-y">
                {metrics.reports_by_template.map((t, i) => (
                  <div
                    key={t.template_name}
                    className="flex items-center justify-between px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium text-gray-400 w-5">
                        {i + 1}.
                      </span>
                      <span className="text-sm text-gray-900 truncate">
                        {t.template_name}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-purple-600">
                      {t.count} relatorio{t.count !== 1 ? 's' : ''}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-8">
                Nenhum dado disponivel
              </p>
            )}
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
