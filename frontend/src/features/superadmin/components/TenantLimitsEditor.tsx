import type { TenantLimits, TenantUsage } from '../types'

interface LimitFieldConfig {
  key: keyof TenantLimits
  label: string
  usageKey?: keyof TenantUsage
  unit?: string
}

const LIMIT_FIELDS: LimitFieldConfig[] = [
  { key: 'max_users', label: 'Max. Usuarios', usageKey: 'users_count' },
  { key: 'max_storage_gb', label: 'Max. Armazenamento', usageKey: 'storage_used_gb', unit: 'GB' },
  { key: 'max_reports_month', label: 'Max. Relatorios/Mes', usageKey: 'reports_this_month' },
]

interface TenantLimitsEditorProps {
  limits: TenantLimits
  onChange: (limits: TenantLimits) => void
  usage?: TenantUsage
  disabled?: boolean
}

export function TenantLimitsEditor({ limits, onChange, usage, disabled }: TenantLimitsEditorProps) {
  const handleChange = (key: keyof TenantLimits, value: string) => {
    const num = parseInt(value, 10)
    if (!isNaN(num) && num > 0) {
      onChange({ ...limits, [key]: num })
    }
  }

  return (
    <div className="space-y-4">
      {LIMIT_FIELDS.map((field) => {
        const currentUsage = usage && field.usageKey ? usage[field.usageKey] : undefined

        return (
          <div key={field.key}>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              {field.label}
              {field.unit && <span className="ml-1 text-xs text-gray-400">({field.unit})</span>}
            </label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                value={limits[field.key]}
                onChange={(e) => handleChange(field.key, e.target.value)}
                disabled={disabled}
                className="w-32 rounded-lg border border-gray-300 px-3 py-2 text-sm disabled:bg-gray-100 disabled:text-gray-500"
              />
              {currentUsage !== undefined && (
                <span className="text-xs text-gray-500">
                  Uso atual: {currentUsage}{field.unit ? ` ${field.unit}` : ''}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
