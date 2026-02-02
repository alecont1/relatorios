import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Loader2,
  Save,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Camera,
} from 'lucide-react'
import {
  reportApi,
  type ReportDetail,
  type UpdateReportData,
  type SnapshotSection,
  type SnapshotField,
} from '@/features/report/api/reportApi'

export function ReportFillPage() {
  const { reportId } = useParams<{ reportId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Form state
  const [infoValues, setInfoValues] = useState<Record<string, string>>({})
  const [responses, setResponses] = useState<Record<string, { value: string; comment: string }>>({})
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())
  const [showComments, setShowComments] = useState<Set<string>>(new Set())
  const [isSaving, setIsSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  // Fetch report details
  const { data: report, isLoading, error } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => reportApi.get(reportId!),
    enabled: !!reportId,
  })

  // Initialize form state from report data
  useEffect(() => {
    if (report) {
      // Initialize info values
      const iv: Record<string, string> = {}
      for (const v of report.info_values) {
        iv[v.field_label] = v.value || ''
      }
      setInfoValues(iv)

      // Initialize responses
      const rs: Record<string, { value: string; comment: string }> = {}
      for (const r of report.checklist_responses) {
        const key = r.field_id || `${r.section_name}:${r.field_label}`
        rs[key] = {
          value: r.response_value || '',
          comment: r.comment || '',
        }
      }
      setResponses(rs)

      // Expand first section by default
      if (report.template_snapshot.sections.length > 0) {
        setExpandedSections(new Set([report.template_snapshot.sections[0].id]))
      }
    }
  }, [report])

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: (data: UpdateReportData) => reportApi.update(reportId!, data),
    onSuccess: () => {
      setLastSaved(new Date())
      queryClient.invalidateQueries({ queryKey: ['report', reportId] })
    },
  })

  // Complete mutation
  const completeMutation = useMutation({
    mutationFn: () => reportApi.complete(reportId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      navigate('/reports')
    },
  })

  // Build update data from form state
  const buildUpdateData = (): UpdateReportData => {
    if (!report) return {}

    // Build info values update
    const infoValuesUpdate = report.template_snapshot.info_fields.map((f) => ({
      info_field_id: f.id,
      field_label: f.label,
      field_type: f.field_type,
      value: infoValues[f.label] || undefined,
    }))

    // Build checklist responses update
    const checklistUpdate = report.template_snapshot.sections.flatMap((section) =>
      section.fields.map((field) => {
        const key = field.id || `${section.name}:${field.label}`
        const response = responses[key] || { value: '', comment: '' }
        return {
          section_id: section.id,
          field_id: field.id,
          section_name: section.name,
          section_order: section.order,
          field_label: field.label,
          field_order: field.order,
          field_type: field.field_type,
          field_options: field.options || undefined,
          response_value: response.value || undefined,
          comment: response.comment || undefined,
        }
      })
    )

    return {
      status: 'in_progress',
      info_values: infoValuesUpdate,
      checklist_responses: checklistUpdate,
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await saveMutation.mutateAsync(buildUpdateData())
    } finally {
      setIsSaving(false)
    }
  }

  const handleComplete = async () => {
    // Save first, then complete
    await handleSave()
    await completeMutation.mutateAsync()
  }

  const toggleSection = (sectionId: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(sectionId)) {
        next.delete(sectionId)
      } else {
        next.add(sectionId)
      }
      return next
    })
  }

  const toggleComment = (fieldKey: string) => {
    setShowComments((prev) => {
      const next = new Set(prev)
      if (next.has(fieldKey)) {
        next.delete(fieldKey)
      } else {
        next.add(fieldKey)
      }
      return next
    })
  }

  // Calculate progress
  const progress = useMemo(() => {
    if (!report) return 0
    const totalFields = report.template_snapshot.sections.reduce(
      (acc, s) => acc + s.fields.length,
      0
    )
    if (totalFields === 0) return 100
    const filledFields = Object.values(responses).filter((r) => r.value).length
    return Math.round((filledFields / totalFields) * 100)
  }, [report, responses])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erro ao carregar relatorio</p>
        <button
          onClick={() => navigate('/reports')}
          className="mt-4 text-blue-600 hover:underline"
        >
          Voltar para lista
        </button>
      </div>
    )
  }

  const isReadOnly = report.status === 'completed' || report.status === 'archived'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/reports')}
            className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5" />
            Voltar
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{report.title}</h1>
            <p className="text-sm text-gray-500">
              Template: {report.template_snapshot.name} | Status: {report.status}
            </p>
          </div>
        </div>

        {!isReadOnly && (
          <div className="flex items-center gap-3">
            {lastSaved && (
              <span className="text-sm text-gray-500">
                Salvo: {lastSaved.toLocaleTimeString('pt-BR')}
              </span>
            )}
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {isSaving ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={handleComplete}
              disabled={completeMutation.isPending || isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" />
              Concluir
            </button>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progresso</span>
          <span className="text-sm text-gray-500">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Info Fields Section */}
      {report.template_snapshot.info_fields.length > 0 && (
        <div className="bg-white p-6 rounded-lg border">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Informacoes do Projeto
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {report.template_snapshot.info_fields.map((field) => (
              <div key={field.id}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                <input
                  type={field.field_type === 'date' ? 'date' : 'text'}
                  value={infoValues[field.label] || ''}
                  onChange={(e) =>
                    setInfoValues((prev) => ({
                      ...prev,
                      [field.label]: e.target.value,
                    }))
                  }
                  placeholder={field.placeholder || ''}
                  disabled={isReadOnly}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Checklist Sections */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Checklist</h2>
        {report.template_snapshot.sections.map((section) => (
          <SectionAccordion
            key={section.id}
            section={section}
            isExpanded={expandedSections.has(section.id)}
            onToggle={() => toggleSection(section.id)}
            responses={responses}
            onResponseChange={(fieldKey, value, comment) => {
              setResponses((prev) => ({
                ...prev,
                [fieldKey]: { ...prev[fieldKey], value, comment: prev[fieldKey]?.comment || '' },
              }))
            }}
            onCommentChange={(fieldKey, comment) => {
              setResponses((prev) => ({
                ...prev,
                [fieldKey]: { ...prev[fieldKey], value: prev[fieldKey]?.value || '', comment },
              }))
            }}
            showComments={showComments}
            onToggleComment={toggleComment}
            isReadOnly={isReadOnly}
          />
        ))}
      </div>
    </div>
  )
}

interface SectionAccordionProps {
  section: SnapshotSection
  isExpanded: boolean
  onToggle: () => void
  responses: Record<string, { value: string; comment: string }>
  onResponseChange: (fieldKey: string, value: string, comment: string) => void
  onCommentChange: (fieldKey: string, comment: string) => void
  showComments: Set<string>
  onToggleComment: (fieldKey: string) => void
  isReadOnly: boolean
}

function SectionAccordion({
  section,
  isExpanded,
  onToggle,
  responses,
  onResponseChange,
  onCommentChange,
  showComments,
  onToggleComment,
  isReadOnly,
}: SectionAccordionProps) {
  // Calculate section completion
  const filledCount = section.fields.filter((f) => {
    const key = f.id || `${section.name}:${f.label}`
    return responses[key]?.value
  }).length

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      {/* Section Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
      >
        <div className="flex items-center gap-3">
          <span className="font-medium text-gray-900">{section.name}</span>
          <span className="text-sm text-gray-500">
            {filledCount}/{section.fields.length} campos
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>

      {/* Section Fields */}
      {isExpanded && (
        <div className="border-t divide-y">
          {section.fields.map((field) => (
            <FieldRow
              key={field.id}
              field={field}
              sectionName={section.name}
              response={responses[field.id || `${section.name}:${field.label}`] || { value: '', comment: '' }}
              onValueChange={(value) =>
                onResponseChange(
                  field.id || `${section.name}:${field.label}`,
                  value,
                  responses[field.id || `${section.name}:${field.label}`]?.comment || ''
                )
              }
              onCommentChange={(comment) =>
                onCommentChange(field.id || `${section.name}:${field.label}`, comment)
              }
              showComment={showComments.has(field.id || `${section.name}:${field.label}`)}
              onToggleComment={() =>
                onToggleComment(field.id || `${section.name}:${field.label}`)
              }
              isReadOnly={isReadOnly}
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface FieldRowProps {
  field: SnapshotField
  sectionName: string
  response: { value: string; comment: string }
  onValueChange: (value: string) => void
  onCommentChange: (comment: string) => void
  showComment: boolean
  onToggleComment: () => void
  isReadOnly: boolean
}

function FieldRow({
  field,
  response,
  onValueChange,
  onCommentChange,
  showComment,
  onToggleComment,
  isReadOnly,
}: FieldRowProps) {
  const hasCommentConfig = field.comment_config?.enabled
  const hasPhotoConfig = field.photo_config?.required || (field.photo_config?.min_count || 0) > 0

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        {/* Field Label */}
        <div className="flex-1">
          <p className="text-sm text-gray-900">{field.label}</p>
          {hasPhotoConfig && (
            <span className="inline-flex items-center gap-1 text-xs text-blue-600 mt-1">
              <Camera className="h-3 w-3" />
              Foto obrigatoria
            </span>
          )}
        </div>

        {/* Field Input */}
        <div className="flex items-center gap-2">
          <FieldInput
            field={field}
            value={response.value}
            onChange={onValueChange}
            isReadOnly={isReadOnly}
          />

          {/* Comment Toggle */}
          {hasCommentConfig && !isReadOnly && (
            <button
              onClick={onToggleComment}
              className={`p-2 rounded ${
                showComment || response.comment
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-400 hover:text-gray-600'
              }`}
              title="Adicionar comentario"
            >
              <MessageSquare className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Comment Field */}
      {(showComment || response.comment) && hasCommentConfig && (
        <div>
          <textarea
            value={response.comment}
            onChange={(e) => onCommentChange(e.target.value)}
            placeholder="Adicione um comentario..."
            disabled={isReadOnly}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
      )}
    </div>
  )
}

interface FieldInputProps {
  field: SnapshotField
  value: string
  onChange: (value: string) => void
  isReadOnly: boolean
}

function FieldInput({ field, value, onChange, isReadOnly }: FieldInputProps) {
  // Parse options for dropdown fields
  const options = field.options
    ? field.options.split(/[,\/]/).map((o) => o.trim()).filter(Boolean)
    : []

  switch (field.field_type) {
    case 'dropdown':
      return (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isReadOnly}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 min-w-[150px]"
        >
          <option value="">Selecione...</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      )

    case 'checkbox':
      return (
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'Sim'}
              onChange={() => onChange('Sim')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">Sim</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'Nao'}
              onChange={() => onChange('Nao')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">Nao</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'N/A'}
              onChange={() => onChange('N/A')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">N/A</span>
          </label>
        </div>
      )

    case 'text':
    default:
      return (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isReadOnly}
          placeholder="Digite..."
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 min-w-[200px]"
        />
      )
  }
}
