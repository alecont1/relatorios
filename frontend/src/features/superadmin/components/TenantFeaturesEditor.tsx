import type { TenantFeatures } from '../types'

interface FeatureFieldConfig {
  key: keyof TenantFeatures
  label: string
  description: string
}

const FEATURE_FIELDS: FeatureFieldConfig[] = [
  {
    key: 'gps_required',
    label: 'GPS Obrigatorio',
    description: 'Exige coordenadas GPS nas fotos dos relatorios.',
  },
  {
    key: 'certificate_required',
    label: 'Certificado Obrigatorio',
    description: 'Exige certificados de calibracao nos instrumentos.',
  },
  {
    key: 'export_excel',
    label: 'Exportar Excel',
    description: 'Permite exportar relatorios em formato Excel.',
  },
  {
    key: 'watermark',
    label: 'Marca d\'Agua',
    description: 'Aplica marca d\'agua nas fotos e relatorios.',
  },
  {
    key: 'custom_pdf',
    label: 'PDF Personalizado',
    description: 'Permite personalizacao do template de PDF.',
  },
]

interface TenantFeaturesEditorProps {
  features: TenantFeatures
  onChange: (features: TenantFeatures) => void
  disabled?: boolean
}

export function TenantFeaturesEditor({ features, onChange, disabled }: TenantFeaturesEditorProps) {
  const handleToggle = (key: keyof TenantFeatures) => {
    onChange({ ...features, [key]: !features[key] })
  }

  return (
    <div className="space-y-3">
      {FEATURE_FIELDS.map((field) => (
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
            aria-checked={features[field.key]}
            aria-label={field.label}
            onClick={() => handleToggle(field.key)}
            disabled={disabled}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
              features[field.key] ? 'bg-blue-600' : 'bg-gray-300'
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                features[field.key] ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      ))}
    </div>
  )
}
