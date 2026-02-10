import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Pause, Play } from 'lucide-react'
import {
  useSuperAdminTenantDetails,
  useUpdateTenantConfig,
  useSuspendTenant,
  useActivateTenant,
  useTenantAuditLog,
  useTenantUsage,
} from '@/features/superadmin/api'
import {
  TenantStatusBadge,
  TenantUsageBar,
  TenantLimitsEditor,
  TenantFeaturesEditor,
  AuditLogTimeline,
  SuspendTenantModal,
} from '@/features/superadmin/components'
import type { TenantLimits, TenantFeatures } from '@/features/superadmin/types'

type TabKey = 'overview' | 'config' | 'audit'

const TABS: { key: TabKey; label: string }[] = [
  { key: 'overview', label: 'Visao Geral' },
  { key: 'config', label: 'Configuracao' },
  { key: 'audit', label: 'Auditoria' },
]

export function SuperAdminTenantDetailsPage() {
  const { tenantId } = useParams<{ tenantId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<TabKey>('overview')
  const [showSuspendModal, setShowSuspendModal] = useState(false)
  const [auditPage, setAuditPage] = useState(1)

  const { data: tenant, isLoading } = useSuperAdminTenantDetails(tenantId ?? '')
  const { data: usage } = useTenantUsage(tenantId ?? '')
  const { data: auditData } = useTenantAuditLog(tenantId ?? '', auditPage)
  const updateConfig = useUpdateTenantConfig(tenantId ?? '')
  const suspendMutation = useSuspendTenant()
  const activateMutation = useActivateTenant()

  const [editLimits, setEditLimits] = useState<TenantLimits | null>(null)
  const [editFeatures, setEditFeatures] = useState<TenantFeatures | null>(null)

  if (isLoading) {
    return <div className="text-gray-500">Carregando detalhes do tenant...</div>
  }

  if (!tenant) {
    return <div className="text-red-500">Tenant nao encontrado.</div>
  }

  const { config } = tenant
  const limits = editLimits ?? config.limits
  const features = editFeatures ?? config.features

  const handleSaveConfig = async () => {
    await updateConfig.mutateAsync({
      ...(editLimits && { limits: editLimits }),
      ...(editFeatures && { features: editFeatures }),
    })
    setEditLimits(null)
    setEditFeatures(null)
  }

  const hasConfigChanges = editLimits !== null || editFeatures !== null

  const handleConfirmSuspend = (reason: string) => {
    suspendMutation.mutate(
      { tenantId: tenant.id, reason },
      { onSuccess: () => setShowSuspendModal(false) }
    )
  }

  const handleActivate = () => {
    activateMutation.mutate(tenant.id)
  }

  return (
    <div>
      {/* Back button */}
      <button
        onClick={() => navigate('/superadmin/tenants')}
        className="mb-4 flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-4 w-4" />
        Voltar para Tenants
      </button>

      {/* Header */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{tenant.name}</h1>
            <TenantStatusBadge
              status={config.status}
              trialEndsAt={config.trial_ends_at}
            />
          </div>
          <p className="mt-1 text-sm text-gray-500">{tenant.slug}</p>
        </div>
        <div className="flex gap-2">
          {config.status !== 'suspended' && (
            <button
              onClick={() => setShowSuspendModal(true)}
              className="flex items-center gap-1 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
            >
              <Pause className="h-4 w-4" />
              Suspender
            </button>
          )}
          {config.status === 'suspended' && (
            <button
              onClick={handleActivate}
              disabled={activateMutation.isPending}
              className="flex items-center gap-1 rounded-lg border border-green-300 px-3 py-2 text-sm font-medium text-green-600 hover:bg-green-50 disabled:opacity-50"
            >
              <Play className="h-4 w-4" />
              Ativar
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-6">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`border-b-2 pb-3 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Info card */}
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-gray-900">
              Informacoes
            </h2>
            <dl className="grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-xs text-gray-500">Nome</dt>
                <dd className="text-sm font-medium text-gray-900">{tenant.name}</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-500">Slug</dt>
                <dd className="text-sm font-medium text-gray-900">{tenant.slug}</dd>
              </div>
              <div>
                <dt className="text-xs text-gray-500">Plano</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {config.plan?.name ?? 'Nenhum'}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-gray-500">Contrato</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {config.contract_type ?? '-'}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-gray-500">Criado em</dt>
                <dd className="text-sm font-medium text-gray-900">
                  {new Date(tenant.created_at).toLocaleDateString('pt-BR')}
                </dd>
              </div>
              {config.suspended_at && (
                <div>
                  <dt className="text-xs text-gray-500">Suspenso em</dt>
                  <dd className="text-sm font-medium text-red-600">
                    {new Date(config.suspended_at).toLocaleDateString('pt-BR')}
                  </dd>
                </div>
              )}
              {config.suspended_reason && (
                <div className="sm:col-span-2">
                  <dt className="text-xs text-gray-500">Motivo da suspensao</dt>
                  <dd className="text-sm text-red-600">{config.suspended_reason}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Usage */}
          {usage && (
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h2 className="mb-4 text-base font-semibold text-gray-900">
                Uso Atual
              </h2>
              <div className="space-y-3">
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
            </div>
          )}
        </div>
      )}

      {activeTab === 'config' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-gray-900">
              Limites
            </h2>
            <TenantLimitsEditor
              limits={limits}
              onChange={setEditLimits}
              usage={usage ?? undefined}
            />
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-base font-semibold text-gray-900">
              Funcionalidades
            </h2>
            <TenantFeaturesEditor
              features={features}
              onChange={setEditFeatures}
            />
          </div>

          {hasConfigChanges && (
            <div className="flex items-center gap-3">
              <button
                onClick={handleSaveConfig}
                disabled={updateConfig.isPending}
                className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {updateConfig.isPending ? 'Salvando...' : 'Salvar Alteracoes'}
              </button>
              <button
                onClick={() => {
                  setEditLimits(null)
                  setEditFeatures(null)
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50"
              >
                Cancelar
              </button>
              {updateConfig.isSuccess && (
                <span className="text-sm text-green-600">Salvo com sucesso!</span>
              )}
              {updateConfig.isError && (
                <span className="text-sm text-red-600">Erro ao salvar.</span>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-4 text-base font-semibold text-gray-900">
            Historico de Auditoria
          </h2>
          {auditData ? (
            <>
              <AuditLogTimeline logs={auditData.items} />
              {auditData.total > auditData.limit && (
                <div className="mt-4 flex items-center justify-center gap-2">
                  <button
                    onClick={() => setAuditPage((p) => Math.max(1, p - 1))}
                    disabled={auditPage <= 1}
                    className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
                  >
                    Anterior
                  </button>
                  <span className="text-sm text-gray-600">
                    Pagina {auditPage}
                  </span>
                  <button
                    onClick={() => setAuditPage((p) => p + 1)}
                    disabled={
                      auditPage >= Math.ceil(auditData.total / auditData.limit)
                    }
                    className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm disabled:opacity-50"
                  >
                    Proxima
                  </button>
                </div>
              )}
            </>
          ) : (
            <p className="text-sm text-gray-500">Carregando auditoria...</p>
          )}
        </div>
      )}

      {/* Suspend modal */}
      <SuspendTenantModal
        tenantName={tenant.name}
        isOpen={showSuspendModal}
        onConfirm={handleConfirmSuspend}
        onClose={() => setShowSuspendModal(false)}
      />
    </div>
  )
}
