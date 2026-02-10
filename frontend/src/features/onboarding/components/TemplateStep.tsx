import { useState } from 'react'
import { FileText, Check, ExternalLink, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useCloneDemoTemplate, useOnboardingStatus } from '../api'

interface TemplateStepProps {
  onComplete: () => void
}

export function TemplateStep({ onComplete }: TemplateStepProps) {
  const { data: status } = useOnboardingStatus()
  const cloneTemplate = useCloneDemoTemplate()
  const [clonedInfo, setClonedInfo] = useState<{ id: string; name: string } | null>(null)

  const existingTemplateId = status?.metadata_json?.demo_template_id as string | undefined

  const handleClone = async () => {
    try {
      const result = await cloneTemplate.mutateAsync()
      setClonedInfo({ id: result.template_id, name: result.template_name })
      onComplete()
    } catch {
      // Error handled by mutation
    }
  }

  if (existingTemplateId && !clonedInfo) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Template de Relatorio</h2>
          <p className="mt-1 text-sm text-gray-500">
            Clone um template demo para comecar rapidamente
          </p>
        </div>
        <div className="rounded-lg border border-green-200 bg-green-50 p-6">
          <div className="flex items-center gap-3">
            <Check className="h-6 w-6 text-green-600" />
            <div>
              <p className="font-medium text-green-900">Template ja clonado</p>
              <Link
                to="/templates"
                className="mt-1 inline-flex items-center gap-1 text-sm text-green-700 hover:underline"
              >
                Ver templates <ExternalLink className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>
        <div className="flex justify-start">
          <button
            onClick={onComplete}
            className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
          >
            Concluir Passo
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Template de Relatorio</h2>
        <p className="mt-1 text-sm text-gray-500">
          Clone um template demo para comecar rapidamente
        </p>
      </div>

      {/* Template preview card */}
      <div className="rounded-lg border bg-white p-6">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">CPQ11 - Comissionamento de Quadros Eletricos</h3>
            <p className="mt-1 text-sm text-gray-500">
              Protocolo completo com 3 secoes e 15 campos de verificacao
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">Verificacao Visual</span>
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">Conexoes e Cabeamento</span>
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs text-gray-600">Testes Funcionais</span>
            </div>
          </div>
        </div>
      </div>

      {clonedInfo && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="flex items-center gap-2">
            <Check className="h-5 w-5 text-green-600" />
            <p className="text-sm font-medium text-green-900">
              Template "{clonedInfo.name}" clonado com sucesso!
            </p>
          </div>
        </div>
      )}

      {cloneTemplate.isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">Erro ao clonar template. Tente novamente.</p>
        </div>
      )}

      <div className="onboarding-template-clone">
        <button
          onClick={handleClone}
          disabled={cloneTemplate.isPending || !!clonedInfo}
          className="rounded-lg bg-blue-600 px-6 py-2.5 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {cloneTemplate.isPending ? (
            <span className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              Clonando...
            </span>
          ) : (
            'Clonar Template Demo'
          )}
        </button>
      </div>
    </div>
  )
}
