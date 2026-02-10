import { useState } from 'react'
import { Loader2, FileText, AlertCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { reportApi, type CreateReportData } from '@/features/report/api/reportApi'
import { useOnboardingStatus } from '../api'

interface FirstReportStepProps {
  onComplete: () => void
}

export function FirstReportStep({ onComplete }: FirstReportStepProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: status } = useOnboardingStatus()
  const [title, setTitle] = useState('')
  const [error, setError] = useState('')

  const demoTemplateId = status?.metadata_json?.demo_template_id as string | undefined

  const createReport = useMutation({
    mutationFn: (data: CreateReportData) => reportApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      onComplete()
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      setError(axiosError.response?.data?.detail || 'Erro ao criar relatorio')
    },
  })

  const handleCreate = () => {
    if (!demoTemplateId || !title.trim()) return

    setError('')
    createReport.mutate({
      template_id: demoTemplateId,
      project_id: '00000000-0000-0000-0000-000000000000',
      title: title.trim(),
    })
  }

  if (!demoTemplateId) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Primeiro Relatorio</h2>
          <p className="mt-1 text-sm text-gray-500">
            Crie seu primeiro relatorio para experimentar o fluxo completo
          </p>
        </div>
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-600" />
            <div>
              <p className="font-medium text-yellow-900">Template nao encontrado</p>
              <p className="mt-1 text-sm text-yellow-700">
                Volte ao passo 2 para clonar o template demo ou pule este passo.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Primeiro Relatorio</h2>
        <p className="mt-1 text-sm text-gray-500">
          Crie seu primeiro relatorio para experimentar o fluxo completo
        </p>
      </div>

      <div className="onboarding-report-form space-y-4 rounded-lg border p-6">
        <div className="flex items-start gap-3 rounded-lg bg-blue-50 p-3">
          <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-blue-900">Template: CPQ11 - Demo</p>
            <p className="text-blue-700">O relatorio sera criado como rascunho</p>
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Titulo do Relatorio *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Ex: Inspecao Quadro Principal - Fevereiro 2026"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        <button
          onClick={handleCreate}
          disabled={createReport.isPending || !title.trim()}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {createReport.isPending ? (
            <span className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Criando...
            </span>
          ) : (
            'Criar Relatorio'
          )}
        </button>
      </div>
    </div>
  )
}
