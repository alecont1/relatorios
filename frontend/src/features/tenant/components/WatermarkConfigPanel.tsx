import { useState, useCallback } from 'react'
import { Settings, Check } from 'lucide-react'
import { useUpdateBranding } from '../api'
import type { WatermarkConfig } from '../types'

const DEFAULT_CONFIG: WatermarkConfig = {
  logo: true,
  gps: true,
  datetime: true,
  company_name: true,
  report_number: false,
  technician_name: true,
}

interface ToggleFieldConfig {
  key: keyof WatermarkConfig
  label: string
  description: string
}

const TOGGLE_FIELDS: ToggleFieldConfig[] = [
  {
    key: 'logo',
    label: 'Logo da Empresa',
    description: 'Exibe o logo da empresa na marca d\'agua das fotos.',
  },
  {
    key: 'gps',
    label: 'Coordenadas GPS',
    description: 'Exibe a latitude e longitude onde a foto foi capturada.',
  },
  {
    key: 'datetime',
    label: 'Data/Hora',
    description: 'Exibe a data e hora em que a foto foi tirada.',
  },
  {
    key: 'company_name',
    label: 'Nome da Empresa',
    description: 'Exibe o nome da empresa na marca d\'agua.',
  },
  {
    key: 'report_number',
    label: 'Numero do Relatorio',
    description: 'Exibe o numero de identificacao do relatorio.',
  },
  {
    key: 'technician_name',
    label: 'Nome do Tecnico',
    description: 'Exibe o nome do tecnico responsavel pela vistoria.',
  },
]

interface WatermarkConfigPanelProps {
  currentConfig: WatermarkConfig | null
  onSaved?: () => void
}

export function WatermarkConfigPanel({ currentConfig, onSaved }: WatermarkConfigPanelProps) {
  const resolvedConfig = currentConfig ?? DEFAULT_CONFIG
  const [config, setConfig] = useState<WatermarkConfig>(resolvedConfig)
  const [showSuccess, setShowSuccess] = useState(false)
  const updateBranding = useUpdateBranding()

  const handleToggle = useCallback((key: keyof WatermarkConfig) => {
    setConfig((prev) => ({ ...prev, [key]: !prev[key] }))
    setShowSuccess(false)
  }, [])

  const handleSave = async () => {
    setShowSuccess(false)
    await updateBranding.mutateAsync({ watermark_config: config })
    setShowSuccess(true)
    onSaved?.()
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
      <div className="mb-4 flex items-center gap-2">
        <Settings className="h-5 w-5 text-gray-600" />
        <h3 className="text-base font-semibold text-gray-900">
          Campos da Marca d'Agua
        </h3>
      </div>

      <p className="mb-5 text-sm text-gray-500">
        Selecione quais informacoes serao exibidas na marca d'agua das fotos dos relatorios.
      </p>

      <div className="space-y-4">
        {TOGGLE_FIELDS.map((field) => (
          <div
            key={field.key}
            className="flex items-center justify-between rounded-lg bg-white px-4 py-3 shadow-sm"
          >
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-900">{field.label}</p>
              <p className="text-xs text-gray-500">{field.description}</p>
            </div>

            <button
              type="button"
              role="switch"
              aria-checked={config[field.key]}
              aria-label={field.label}
              onClick={() => handleToggle(field.key)}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                config[field.key] ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  config[field.key] ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        ))}
      </div>

      <div className="mt-5 flex items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={updateBranding.isPending}
          className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {updateBranding.isPending ? 'Salvando...' : 'Salvar Configuracao'}
        </button>

        {showSuccess && (
          <span className="flex items-center gap-1 text-sm text-green-600">
            <Check className="h-4 w-4" />
            Configuracao salva com sucesso!
          </span>
        )}

        {updateBranding.isError && (
          <span className="text-sm text-red-600">
            Erro ao salvar. Tente novamente.
          </span>
        )}
      </div>
    </div>
  )
}
