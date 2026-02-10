import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, Building2 } from 'lucide-react'
import { useCreateTenantWithConfig, useTenantPlans } from '@/features/superadmin/api'
import { PlanSelector } from '@/features/superadmin/components'
import type { CreateTenantWithConfig } from '@/features/superadmin/types'

const STEPS = [
  'Dados da Empresa',
  'Plano',
  'Admin Inicial',
  'Revisao',
]

function slugify(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

type FormData = {
  name: string
  slug: string
  contract_type: string
  plan_id: string
  trial_days: number
  admin_email: string
  admin_full_name: string
  admin_password: string
  brand_color_primary: string
}

const INITIAL_DATA: FormData = {
  name: '',
  slug: '',
  contract_type: '',
  plan_id: '',
  trial_days: 14,
  admin_email: '',
  admin_full_name: '',
  admin_password: '',
  brand_color_primary: '',
}

export function CreateTenantWizard() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState<FormData>(INITIAL_DATA)
  const [slugManual, setSlugManual] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { data: plans } = useTenantPlans()
  const createMutation = useCreateTenantWithConfig()

  const updateField = <K extends keyof FormData>(key: K, value: FormData[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setError(null)
  }

  const handleNameChange = (name: string) => {
    updateField('name', name)
    if (!slugManual) {
      updateField('slug', slugify(name))
    }
  }

  const canAdvance = (): boolean => {
    switch (step) {
      case 0:
        return form.name.trim().length >= 2 && form.slug.trim().length >= 2
      case 1:
        return !!form.plan_id
      case 2:
        return (
          form.admin_email.includes('@') &&
          form.admin_full_name.trim().length >= 2 &&
          form.admin_password.length >= 8
        )
      default:
        return true
    }
  }

  const handleNext = () => {
    if (!canAdvance()) {
      setError('Preencha todos os campos obrigatorios.')
      return
    }
    setError(null)
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
  }

  const handleBack = () => {
    setError(null)
    setStep((s) => Math.max(s - 1, 0))
  }

  const handleSubmit = async () => {
    const payload: CreateTenantWithConfig = {
      name: form.name.trim(),
      slug: form.slug.trim(),
      plan_id: form.plan_id,
      admin_email: form.admin_email.trim(),
      admin_password: form.admin_password,
      admin_full_name: form.admin_full_name.trim(),
      ...(form.contract_type && { contract_type: form.contract_type }),
      ...(form.trial_days && { trial_days: form.trial_days }),
      ...(form.brand_color_primary && { brand_color_primary: form.brand_color_primary }),
    }

    try {
      const result = await createMutation.mutateAsync(payload)
      navigate(`/superadmin/tenants/${result.id}`)
    } catch {
      setError('Erro ao criar tenant. Verifique os dados e tente novamente.')
    }
  }

  const selectedPlan = plans?.find((p) => p.id === form.plan_id)

  return (
    <div>
      <div className="mb-6">
        <button
          onClick={() => navigate('/superadmin/tenants')}
          className="mb-4 flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-4 w-4" />
          Voltar para Tenants
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Novo Tenant</h1>
      </div>

      {/* Progress indicator */}
      <div className="mb-8 flex items-center gap-2">
        {STEPS.map((label, i) => (
          <div key={label} className="flex items-center gap-2">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                i < step
                  ? 'bg-green-100 text-green-700'
                  : i === step
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-400'
              }`}
            >
              {i < step ? <Check className="h-4 w-4" /> : i + 1}
            </div>
            <span
              className={`hidden text-sm sm:inline ${
                i === step ? 'font-medium text-gray-900' : 'text-gray-400'
              }`}
            >
              {label}
            </span>
            {i < STEPS.length - 1 && (
              <div className="mx-1 h-px w-6 bg-gray-300" />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        {step === 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Dados da Empresa
            </h2>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Nome da Empresa <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => handleNameChange(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="Nome da empresa"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Slug <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.slug}
                onChange={(e) => {
                  setSlugManual(true)
                  updateField('slug', e.target.value)
                }}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="slug-da-empresa"
              />
              <p className="mt-1 text-xs text-gray-500">
                Identificador unico. Gerado automaticamente a partir do nome.
              </p>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Tipo de Contrato
              </label>
              <input
                type="text"
                value={form.contract_type}
                onChange={(e) => updateField('contract_type', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="Ex: mensal, anual, enterprise"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Cor Primaria da Marca
              </label>
              <input
                type="color"
                value={form.brand_color_primary || '#3B82F6'}
                onChange={(e) => updateField('brand_color_primary', e.target.value)}
                className="h-10 w-20 cursor-pointer rounded border border-gray-300"
              />
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Selecionar Plano
            </h2>
            {plans ? (
              <PlanSelector
                plans={plans}
                selectedPlanId={form.plan_id}
                onChange={(id) => updateField('plan_id', id)}
                showDetails
              />
            ) : (
              <p className="text-sm text-gray-500">Carregando planos...</p>
            )}
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Dias de Trial
              </label>
              <input
                type="number"
                min={0}
                value={form.trial_days}
                onChange={(e) =>
                  updateField('trial_days', parseInt(e.target.value, 10) || 0)
                }
                className="w-32 rounded-lg border border-gray-300 px-3 py-2"
              />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Administrador Inicial
            </h2>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Nome Completo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.admin_full_name}
                onChange={(e) => updateField('admin_full_name', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="Nome completo do administrador"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={form.admin_email}
                onChange={(e) => updateField('admin_email', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="admin@empresa.com"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Senha <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={form.admin_password}
                onChange={(e) => updateField('admin_password', e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="Minimo 8 caracteres"
              />
              <p className="mt-1 text-xs text-gray-500">
                A senha deve ter no minimo 8 caracteres.
              </p>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Revisao
            </h2>
            <div className="rounded-lg bg-gray-50 p-4 space-y-3">
              <div className="flex items-center gap-3">
                <Building2 className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{form.name}</p>
                  <p className="text-xs text-gray-500">{form.slug}</p>
                </div>
              </div>
              {form.contract_type && (
                <p className="text-sm text-gray-600">
                  Contrato: <span className="font-medium">{form.contract_type}</span>
                </p>
              )}
              {selectedPlan && (
                <p className="text-sm text-gray-600">
                  Plano: <span className="font-medium">{selectedPlan.name}</span>
                  {selectedPlan.price_display && ` - ${selectedPlan.price_display}`}
                </p>
              )}
              <p className="text-sm text-gray-600">
                Trial: <span className="font-medium">{form.trial_days} dias</span>
              </p>
              <div className="border-t border-gray-200 pt-3">
                <p className="text-xs font-medium uppercase text-gray-500">
                  Administrador
                </p>
                <p className="text-sm text-gray-900">{form.admin_full_name}</p>
                <p className="text-sm text-gray-600">{form.admin_email}</p>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <p className="mt-4 text-sm text-red-600">{error}</p>
        )}

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <button
            type="button"
            onClick={handleBack}
            disabled={step === 0}
            className="flex items-center gap-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:invisible"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar
          </button>

          {step < STEPS.length - 1 ? (
            <button
              type="button"
              onClick={handleNext}
              className="flex items-center gap-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Proximo
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={createMutation.isPending}
              className="flex items-center gap-1 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Criando...' : 'Criar Tenant'}
              <Check className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
