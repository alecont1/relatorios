import type { SnapshotInfoField } from '@/features/report/api/reportApi'

interface InfoFieldsStepProps {
  infoFields: SnapshotInfoField[]
  infoValues: Record<string, string>
  onInfoValueChange: (label: string, value: string) => void
  isReadOnly: boolean
}

export function InfoFieldsStep({
  infoFields,
  infoValues,
  onInfoValueChange,
  isReadOnly,
}: InfoFieldsStepProps) {
  if (infoFields.length === 0) return null

  return (
    <div className="bg-white p-6 rounded-lg border">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Informacoes do Projeto
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        {infoFields.map((field) => (
          <div key={field.id}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              type={field.field_type === 'date' ? 'date' : 'text'}
              value={infoValues[field.label] || ''}
              onChange={(e) => onInfoValueChange(field.label, e.target.value)}
              placeholder={field.placeholder || ''}
              disabled={isReadOnly}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
          </div>
        ))}
      </div>
    </div>
  )
}
