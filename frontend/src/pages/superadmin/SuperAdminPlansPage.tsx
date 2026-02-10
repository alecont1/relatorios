import { useState } from 'react'
import { Plus, Pencil, X, Check } from 'lucide-react'
import {
  useTenantPlans,
  useCreatePlan,
  useUpdatePlan,
} from '@/features/superadmin/api'
import type {
  TenantPlan,
  CreatePlanRequest,
  TenantLimits,
  TenantFeatures,
} from '@/features/superadmin/types'
import {
  TenantLimitsEditor,
  TenantFeaturesEditor,
} from '@/features/superadmin/components'

const DEFAULT_LIMITS: TenantLimits = {
  max_users: 10,
  max_storage_gb: 5,
  max_reports_month: 100,
}

const DEFAULT_FEATURES: TenantFeatures = {
  gps_required: false,
  certificate_required: false,
  export_excel: false,
  watermark: true,
  custom_pdf: false,
}

interface PlanFormData {
  name: string
  description: string
  limits: TenantLimits
  features: TenantFeatures
  price_display: string
  is_active: boolean
}

const INITIAL_FORM: PlanFormData = {
  name: '',
  description: '',
  limits: DEFAULT_LIMITS,
  features: DEFAULT_FEATURES,
  price_display: '',
  is_active: true,
}

export function SuperAdminPlansPage() {
  const { data: plans, isLoading } = useTenantPlans()
  const createPlan = useCreatePlan()
  const updatePlan = useUpdatePlan()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingPlan, setEditingPlan] = useState<TenantPlan | null>(null)
  const [form, setForm] = useState<PlanFormData>(INITIAL_FORM)
  const [error, setError] = useState<string | null>(null)

  const openCreate = () => {
    setForm(INITIAL_FORM)
    setEditingPlan(null)
    setError(null)
    setShowCreateModal(true)
  }

  const openEdit = (plan: TenantPlan) => {
    setForm({
      name: plan.name,
      description: plan.description ?? '',
      limits: plan.limits,
      features: plan.features,
      price_display: plan.price_display ?? '',
      is_active: plan.is_active,
    })
    setEditingPlan(plan)
    setError(null)
    setShowCreateModal(true)
  }

  const closeModal = () => {
    setShowCreateModal(false)
    setEditingPlan(null)
    setError(null)
  }

  const handleSubmit = async () => {
    if (!form.name.trim()) {
      setError('Nome do plano e obrigatorio.')
      return
    }

    const payload: CreatePlanRequest = {
      name: form.name.trim(),
      ...(form.description && { description: form.description.trim() }),
      limits: form.limits,
      features: form.features,
      ...(form.price_display && { price_display: form.price_display.trim() }),
      is_active: form.is_active,
    }

    try {
      if (editingPlan) {
        await updatePlan.mutateAsync({ id: editingPlan.id, ...payload })
      } else {
        await createPlan.mutateAsync(payload)
      }
      closeModal()
    } catch {
      setError('Erro ao salvar plano. Tente novamente.')
    }
  }

  const isPending = createPlan.isPending || updatePlan.isPending

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Planos</h1>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          Novo Plano
        </button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-48 animate-pulse rounded-xl border border-gray-200 bg-gray-100"
            />
          ))}
        </div>
      ) : plans && plans.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <PlanCard key={plan.id} plan={plan} onEdit={openEdit} />
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-gray-200 bg-white py-12 text-center">
          <p className="text-gray-500">Nenhum plano cadastrado.</p>
        </div>
      )}

      {/* Create/Edit modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div
            className="fixed inset-0 bg-black/50 transition-opacity"
            onClick={closeModal}
          />
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="relative w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  {editingPlan ? 'Editar Plano' : 'Novo Plano'}
                </h2>
                <button
                  onClick={closeModal}
                  className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="max-h-[70vh] space-y-4 overflow-y-auto">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Nome <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.name}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, name: e.target.value }))
                    }
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    placeholder="Nome do plano"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Descricao
                  </label>
                  <textarea
                    value={form.description}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, description: e.target.value }))
                    }
                    rows={2}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                    placeholder="Descricao do plano"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Preco (exibicao)
                  </label>
                  <input
                    type="text"
                    value={form.price_display}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, price_display: e.target.value }))
                    }
                    className="w-full rounded-lg border border-gray-300 px-3 py-2"
                    placeholder="Ex: R$ 99/mes"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Limites
                  </label>
                  <TenantLimitsEditor
                    limits={form.limits}
                    onChange={(limits) =>
                      setForm((prev) => ({ ...prev, limits }))
                    }
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Funcionalidades
                  </label>
                  <TenantFeaturesEditor
                    features={form.features}
                    onChange={(features) =>
                      setForm((prev) => ({ ...prev, features }))
                    }
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, is_active: e.target.checked }))
                    }
                    className="rounded border-gray-300"
                    id="plan-active"
                  />
                  <label
                    htmlFor="plan-active"
                    className="text-sm text-gray-700"
                  >
                    Plano ativo (visivel para selecao)
                  </label>
                </div>
              </div>

              {error && (
                <p className="mt-3 text-sm text-red-600">{error}</p>
              )}

              <div className="mt-5 flex justify-end gap-3">
                <button
                  onClick={closeModal}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={isPending}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {isPending ? 'Salvando...' : editingPlan ? 'Salvar' : 'Criar Plano'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function PlanCard({
  plan,
  onEdit,
}: {
  plan: TenantPlan
  onEdit: (plan: TenantPlan) => void
}) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-start justify-between">
        <div>
          <h3 className="text-base font-semibold text-gray-900">{plan.name}</h3>
          {plan.price_display && (
            <p className="text-sm font-medium text-blue-600">{plan.price_display}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              plan.is_active
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-500'
            }`}
          >
            {plan.is_active ? 'Ativo' : 'Inativo'}
          </span>
          <button
            onClick={() => onEdit(plan)}
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            <Pencil className="h-4 w-4" />
          </button>
        </div>
      </div>

      {plan.description && (
        <p className="mb-3 text-xs text-gray-500">{plan.description}</p>
      )}

      <div className="space-y-1 text-xs text-gray-600">
        <p>{plan.limits.max_users} usuarios</p>
        <p>{plan.limits.max_storage_gb} GB armazenamento</p>
        <p>{plan.limits.max_reports_month} relatorios/mes</p>
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {plan.features.export_excel && (
          <FeatureTag label="Excel" active />
        )}
        {plan.features.watermark && (
          <FeatureTag label="Watermark" active />
        )}
        {plan.features.custom_pdf && (
          <FeatureTag label="PDF" active />
        )}
        {plan.features.gps_required && (
          <FeatureTag label="GPS" active />
        )}
        {plan.features.certificate_required && (
          <FeatureTag label="Certificado" active />
        )}
      </div>
    </div>
  )
}

function FeatureTag({ label, active }: { label: string; active: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] ${
        active ? 'bg-blue-50 text-blue-700' : 'bg-gray-100 text-gray-500'
      }`}
    >
      {active && <Check className="h-2.5 w-2.5" />}
      {label}
    </span>
  )
}
