import { useState, useEffect, useMemo, useCallback } from 'react'
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
  Cloud,
  CloudOff,
  RefreshCw,
  FileDown,
} from 'lucide-react'
import {
  reportApi,
  type ReportDetail,
  type UpdateReportData,
  type SnapshotSection,
  type SnapshotField,
} from '@/features/report/api/reportApi'
import { useAutoSave } from '@/features/report/hooks'
import {
  CameraCapture,
  PhotoGallery,
  photoApi,
  type CaptureMetadata,
  type PhotoMetadata,
} from '@/features/photo'

export function ReportFillPage() {
  const { reportId } = useParams<{ reportId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Form state
  const [infoValues, setInfoValues] = useState<Record<string, string>>({})
  const [responses, setResponses] = useState<Record<string, { value: string; comment: string }>>({})
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())
  const [showComments, setShowComments] = useState<Set<string>>(new Set())
  const [isInitialized, setIsInitialized] = useState(false)
  const [showDraftRecovery, setShowDraftRecovery] = useState(false)

  // Photo state
  const [photos, setPhotos] = useState<Record<string, PhotoMetadata[]>>({})
  const [cameraOpen, setCameraOpen] = useState(false)
  const [cameraResponseId, setCameraResponseId] = useState<string | null>(null)

  // PDF download state
  const [isDownloading, setIsDownloading] = useState(false)

  // Fetch report details
  const { data: report, isLoading, error } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => reportApi.get(reportId!),
    enabled: !!reportId,
  })

  // Build update data from form state
  const buildUpdateData = useCallback((): UpdateReportData => {
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
  }, [report, infoValues, responses])

  // Form data for auto-save change detection
  const formData = useMemo(
    () => ({ infoValues, responses }),
    [infoValues, responses]
  )

  // Draft storage key
  const draftKey = reportId ? `report-draft-${reportId}` : undefined

  // Auto-save hook
  const autoSave = useAutoSave({
    data: formData,
    onSave: async () => {
      const data = buildUpdateData()
      await reportApi.update(reportId!, data)
      queryClient.invalidateQueries({ queryKey: ['report', reportId] })
    },
    debounceMs: 2000,
    enabled: isInitialized && report?.status !== 'completed' && report?.status !== 'archived',
    storageKey: draftKey,
  })

  // Initialize form state from report data
  useEffect(() => {
    if (report && !isInitialized) {
      // Check for draft backup first
      const draft = autoSave.loadDraftBackup()
      if (draft && (draft.infoValues || draft.responses)) {
        setShowDraftRecovery(true)
      }

      // Initialize info values from server
      const iv: Record<string, string> = {}
      for (const v of report.info_values) {
        iv[v.field_label] = v.value || ''
      }
      setInfoValues(iv)

      // Initialize responses and photos from server
      const rs: Record<string, { value: string; comment: string }> = {}
      const ph: Record<string, PhotoMetadata[]> = {}
      for (const r of report.checklist_responses) {
        const key = r.field_id || `${r.section_name}:${r.field_label}`
        rs[key] = {
          value: r.response_value || '',
          comment: r.comment || '',
        }
        // Initialize photos for this response
        if (r.photos && r.photos.length > 0) {
          ph[String(r.id)] = r.photos as PhotoMetadata[]
        }
      }
      setResponses(rs)
      setPhotos(ph)

      // Expand first section by default
      if (report.template_snapshot.sections.length > 0) {
        setExpandedSections(new Set([report.template_snapshot.sections[0].id]))
      }

      setIsInitialized(true)
    }
  }, [report, isInitialized, autoSave])

  // Recover draft from localStorage
  const recoverDraft = useCallback(() => {
    const draft = autoSave.loadDraftBackup()
    if (draft) {
      if (draft.infoValues) setInfoValues(draft.infoValues)
      if (draft.responses) setResponses(draft.responses)
    }
    setShowDraftRecovery(false)
  }, [autoSave])

  const dismissDraftRecovery = useCallback(() => {
    autoSave.clearDraftBackup()
    setShowDraftRecovery(false)
  }, [autoSave])

  // Complete mutation
  const completeMutation = useMutation({
    mutationFn: () => reportApi.complete(reportId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      navigate('/reports')
    },
  })

  // Manual save handler
  const handleSave = async () => {
    await autoSave.saveNow()
  }

  // Complete handler
  const handleComplete = async () => {
    // Save first, then complete
    await autoSave.saveNow()
    await completeMutation.mutateAsync()
  }

  // PDF download handler
  const handleDownloadPdf = async () => {
    if (!report || !reportId) return

    setIsDownloading(true)
    try {
      const filename = `${report.title.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
      await reportApi.downloadPdf(reportId, filename)
    } catch (error) {
      console.error('Failed to download PDF:', error)
    } finally {
      setIsDownloading(false)
    }
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

  // Photo handlers
  const openCamera = useCallback((responseId: string) => {
    setCameraResponseId(responseId)
    setCameraOpen(true)
  }, [])

  const handlePhotoCapture = useCallback(async (blob: Blob, metadata: CaptureMetadata) => {
    if (!cameraResponseId || !reportId) return

    try {
      const photo = await photoApi.upload(reportId, {
        response_id: cameraResponseId,
        file: blob,
        captured_at: metadata.capturedAt,
        latitude: metadata.gps?.latitude,
        longitude: metadata.gps?.longitude,
        gps_accuracy: metadata.gps?.accuracy,
        address: metadata.address,
      })

      setPhotos((prev) => ({
        ...prev,
        [cameraResponseId]: [...(prev[cameraResponseId] || []), photo],
      }))
    } catch (error) {
      console.error('Failed to upload photo:', error)
    }
  }, [cameraResponseId, reportId])

  const handlePhotoDelete = useCallback(async (responseId: string, photoId: string) => {
    if (!reportId) return

    try {
      await photoApi.delete(reportId, photoId)
      setPhotos((prev) => ({
        ...prev,
        [responseId]: (prev[responseId] || []).filter((p) => p.id !== photoId),
      }))
    } catch (error) {
      console.error('Failed to delete photo:', error)
    }
  }, [reportId])

  // Get response ID from field
  const getResponseId = useCallback((fieldId: string | undefined, sectionName: string, fieldLabel: string): string | undefined => {
    if (!report) return undefined
    const key = fieldId || `${sectionName}:${fieldLabel}`
    const response = report.checklist_responses.find(
      (r) => (r.field_id === fieldId) || `${r.section_name}:${r.field_label}` === key
    )
    return response ? String(response.id) : undefined
  }, [report])

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
            {/* Auto-save status indicator */}
            <AutoSaveStatus
              status={autoSave.status}
              lastSaved={autoSave.lastSaved}
              error={autoSave.error}
            />
            <button
              onClick={handleSave}
              disabled={autoSave.isSaving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {autoSave.isSaving ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={handleComplete}
              disabled={completeMutation.isPending || autoSave.isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" />
              Concluir
            </button>
          </div>
        )}

        {isReadOnly && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {report.status === 'completed' ? 'Relatorio concluido' : 'Relatorio arquivado'}
            </span>
            <button
              onClick={handleDownloadPdf}
              disabled={isDownloading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isDownloading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileDown className="h-4 w-4" />
              )}
              {isDownloading ? 'Baixando...' : 'Baixar PDF'}
            </button>
          </div>
        )}
      </div>

      {/* Draft Recovery Banner */}
      {showDraftRecovery && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <RefreshCw className="h-5 w-5 text-yellow-600" />
            <p className="text-sm text-yellow-800">
              Foi encontrado um rascunho nao salvo. Deseja recuperar?
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={dismissDraftRecovery}
              className="px-3 py-1 text-sm text-yellow-700 hover:bg-yellow-100 rounded"
            >
              Descartar
            </button>
            <button
              onClick={recoverDraft}
              className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
            >
              Recuperar
            </button>
          </div>
        </div>
      )}

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
            photos={photos}
            getResponseId={getResponseId}
            onOpenCamera={openCamera}
            onDeletePhoto={handlePhotoDelete}
          />
        ))}
      </div>

      {/* Camera Capture Modal */}
      <CameraCapture
        isOpen={cameraOpen}
        onClose={() => setCameraOpen(false)}
        onCapture={handlePhotoCapture}
        requireGPS={false}
      />
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
  photos: Record<string, PhotoMetadata[]>
  getResponseId: (fieldId: string | undefined, sectionName: string, fieldLabel: string) => string | undefined
  onOpenCamera: (responseId: string) => void
  onDeletePhoto: (responseId: string, photoId: string) => void
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
  photos,
  getResponseId,
  onOpenCamera,
  onDeletePhoto,
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
          {section.fields.map((field) => {
            const responseId = getResponseId(field.id, section.name, field.label)
            return (
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
                photos={responseId ? photos[responseId] || [] : []}
                responseId={responseId}
                onOpenCamera={onOpenCamera}
                onDeletePhoto={onDeletePhoto}
              />
            )
          })}
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
  photos: PhotoMetadata[]
  responseId?: string
  onOpenCamera: (responseId: string) => void
  onDeletePhoto: (responseId: string, photoId: string) => void
}

function FieldRow({
  field,
  response,
  onValueChange,
  onCommentChange,
  showComment,
  onToggleComment,
  isReadOnly,
  photos,
  responseId,
  onOpenCamera,
  onDeletePhoto,
}: FieldRowProps) {
  const hasCommentConfig = field.comment_config?.enabled
  const photoConfig = field.photo_config
  const hasPhotoConfig = photoConfig && (photoConfig.required || (photoConfig.min_count || 0) > 0 || (photoConfig.max_count || 0) > 0)

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        {/* Field Label */}
        <div className="flex-1">
          <p className="text-sm text-gray-900">{field.label}</p>
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

      {/* Photo Gallery */}
      {(hasPhotoConfig || photos.length > 0) && responseId && (
        <PhotoGallery
          photos={photos}
          maxPhotos={photoConfig?.max_count}
          required={photoConfig?.required || (photoConfig?.min_count || 0) > 0}
          onAddPhoto={() => onOpenCamera(responseId)}
          onDeletePhoto={(photoId) => onDeletePhoto(responseId, photoId)}
          isReadOnly={isReadOnly}
        />
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

// Auto-save status indicator component
interface AutoSaveStatusProps {
  status: 'idle' | 'pending' | 'saving' | 'saved' | 'error'
  lastSaved: Date | null
  error: string | null
}

function AutoSaveStatus({ status, lastSaved, error }: AutoSaveStatusProps) {
  const formatTime = (date: Date) => date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  switch (status) {
    case 'pending':
      return (
        <span className="flex items-center gap-1.5 text-sm text-gray-400">
          <Cloud className="h-4 w-4" />
          Alteracoes pendentes...
        </span>
      )
    case 'saving':
      return (
        <span className="flex items-center gap-1.5 text-sm text-blue-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Salvando...
        </span>
      )
    case 'saved':
      return (
        <span className="flex items-center gap-1.5 text-sm text-green-600">
          <Cloud className="h-4 w-4" />
          Salvo {lastSaved && `as ${formatTime(lastSaved)}`}
        </span>
      )
    case 'error':
      return (
        <span className="flex items-center gap-1.5 text-sm text-red-500" title={error || undefined}>
          <CloudOff className="h-4 w-4" />
          Erro ao salvar
        </span>
      )
    default:
      return null
  }
}
