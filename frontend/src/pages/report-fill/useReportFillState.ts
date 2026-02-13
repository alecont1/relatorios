import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  reportApi,
  type UpdateReportData,
  type ReportDetail,
} from '@/features/report/api/reportApi'
import { useAutoSave } from '@/features/report/hooks'
import {
  photoApi,
  type CaptureMetadata,
  type PhotoMetadata,
} from '@/features/photo'
import {
  signatureApi,
  type SignatureData,
} from '@/features/signature'
import { type Certificate } from '@/features/report/components/CertificateSelectionModal'
import { useTenantStore, getLogoUrl } from '@/features/tenant'

export interface ReportFillState {
  // Route & navigation
  reportId: string | undefined
  navigate: ReturnType<typeof useNavigate>

  // Report data
  report: ReportDetail | undefined
  isLoading: boolean
  error: Error | null

  // Tenant branding
  tenantLogo: string | undefined
  watermarkText: string | undefined

  // Form state
  infoValues: Record<string, string>
  setInfoValues: React.Dispatch<React.SetStateAction<Record<string, string>>>
  responses: Record<string, { value: string; comment: string }>
  setResponses: React.Dispatch<React.SetStateAction<Record<string, { value: string; comment: string }>>>
  expandedSections: Set<string>
  showComments: Set<string>
  isInitialized: boolean
  showDraftRecovery: boolean

  // Photo state
  photos: Record<string, PhotoMetadata[]>
  cameraOpen: boolean
  setCameraOpen: (open: boolean) => void
  cameraResponseId: string | null

  // PDF download state
  isDownloading: boolean

  // Signature state
  signatures: SignatureData[]

  // Certificate modal state
  showCertificateModal: boolean
  setShowCertificateModal: (show: boolean) => void
  isCompleting: boolean

  // Auto-save
  autoSave: ReturnType<typeof useAutoSave>

  // Computed
  isReadOnly: boolean
  progress: number

  // Actions
  toggleSection: (sectionId: string) => void
  toggleComment: (fieldKey: string) => void
  handleSave: () => Promise<void>
  handlePreFillAll: () => void
  handleOpenCompleteModal: () => Promise<void>
  handleComplete: (certificates: Certificate[]) => Promise<void>
  handleDownloadPdf: () => Promise<void>
  recoverDraft: () => void
  dismissDraftRecovery: () => void

  // Photo actions
  openCamera: (responseId: string) => void
  handlePhotoCapture: (blob: Blob, metadata: CaptureMetadata) => Promise<void>
  handlePhotoDelete: (responseId: string, photoId: string) => Promise<void>
  getResponseId: (fieldId: string | undefined, sectionName: string, fieldLabel: string) => string | undefined

  // Signature actions
  handleAddSignature: (roleName: string, blob: Blob, signerName?: string, fieldId?: string) => Promise<void>
  handleDeleteSignature: (signatureId: string) => Promise<void>

  // Complete mutation (for loading state in UI)
  completeMutation: ReturnType<typeof useMutation<ReportDetail, Error>>
}

export function useReportFillState(): ReportFillState {
  const { reportId } = useParams<{ reportId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Get tenant branding for watermark
  const { branding } = useTenantStore()
  const tenantLogo = getLogoUrl(branding?.logo_primary_key)
  const watermarkText = branding?.watermark_text || undefined

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

  // Signature state
  const [signatures, setSignatures] = useState<SignatureData[]>([])

  // Certificate selection modal state
  const [showCertificateModal, setShowCertificateModal] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)

  // Track save-in-progress to prevent race conditions
  const saveInProgressRef = useRef(false)

  // Fetch report details
  const { data: report, isLoading, error } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => reportApi.get(reportId!),
    enabled: !!reportId,
  })

  // Fetch signatures
  const { data: signaturesData } = useQuery({
    queryKey: ['signatures', reportId],
    queryFn: () => signatureApi.list(reportId!),
    enabled: !!reportId,
  })

  // Update signatures state when data changes
  useEffect(() => {
    if (signaturesData) {
      setSignatures(signaturesData.signatures)
    }
  }, [signaturesData])

  // Build update data from form state
  const buildUpdateData = useCallback((): UpdateReportData => {
    if (!report) return {}

    const infoValuesUpdate = report.template_snapshot.info_fields.map((f) => ({
      info_field_id: f.id,
      field_label: f.label,
      field_type: f.field_type,
      value: infoValues[f.label] || undefined,
    }))

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

  // Auto-save hook with race condition guard
  const autoSave = useAutoSave({
    data: formData,
    onSave: async () => {
      if (saveInProgressRef.current) return
      saveInProgressRef.current = true
      try {
        const data = buildUpdateData()
        await reportApi.update(reportId!, data)
        queryClient.invalidateQueries({ queryKey: ['report', reportId] })
      } finally {
        saveInProgressRef.current = false
      }
    },
    debounceMs: 2000,
    enabled: isInitialized && !isCompleting && report?.status !== 'completed' && report?.status !== 'archived',
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
        if (r.photos && r.photos.length > 0) {
          ph[String(r.id)] = r.photos.map(p => ({
            id: p.photo_id,
            url: p.url,
            captured_at: new Date().toISOString(),
            watermarked: true,
            ...(p.caption && { caption: p.caption }),
          })) as PhotoMetadata[]
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
      queryClient.invalidateQueries({ queryKey: ['report', reportId] })
      navigate('/reports')
    },
  })

  // Manual save handler
  const handleSave = useCallback(async () => {
    await autoSave.saveNow()
  }, [autoSave])

  // Open certificate modal before completing
  const handleOpenCompleteModal = useCallback(async () => {
    await autoSave.saveNow()
    setShowCertificateModal(true)
  }, [autoSave])

  // Complete handler (called after certificate selection)
  const handleComplete = useCallback(async (certificates: Certificate[]) => {
    // certificates are already linked via the modal API call
    void certificates
    setShowCertificateModal(false)
    setIsCompleting(true)

    try {
      await completeMutation.mutateAsync()
    } catch (err) {
      console.log('Report completion error (may already be completed):', err)
      navigate('/reports')
    }
  }, [completeMutation, navigate])

  // Pre-fill all checklist fields with first positive option
  const handlePreFillAll = useCallback(() => {
    if (!report) return

    const newResponses = { ...responses }

    for (const section of report.template_snapshot.sections) {
      for (const field of section.fields) {
        const key = field.id || `${section.name}:${field.label}`

        if (field.field_type === 'dropdown' && field.options) {
          const options = field.options.split(/[,\/]/).map((o) => o.trim()).filter(Boolean)
          if (options.length > 0) {
            newResponses[key] = {
              value: options[0],
              comment: responses[key]?.comment || '',
            }
          }
        }
      }
    }

    setResponses(newResponses)
  }, [report, responses])

  // PDF download handler
  const handleDownloadPdf = useCallback(async () => {
    if (!report || !reportId) return

    setIsDownloading(true)
    try {
      const filename = `${report.title.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
      await reportApi.downloadPdf(reportId, filename)
    } catch (err) {
      console.error('Failed to download PDF:', err)
    } finally {
      setIsDownloading(false)
    }
  }, [report, reportId])

  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(sectionId)) {
        next.delete(sectionId)
      } else {
        next.add(sectionId)
      }
      return next
    })
  }, [])

  const toggleComment = useCallback((fieldKey: string) => {
    setShowComments((prev) => {
      const next = new Set(prev)
      if (next.has(fieldKey)) {
        next.delete(fieldKey)
      } else {
        next.add(fieldKey)
      }
      return next
    })
  }, [])

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
    } catch (err) {
      console.error('Failed to upload photo:', err)
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
    } catch (err) {
      console.error('Failed to delete photo:', err)
    }
  }, [reportId])

  // Signature handlers
  const handleAddSignature = useCallback(async (
    roleName: string,
    blob: Blob,
    signerName?: string,
    fieldId?: string
  ) => {
    if (!reportId) return

    const newSignature = await signatureApi.upload(reportId, {
      role_name: roleName,
      file: blob,
      signer_name: signerName,
      signature_field_id: fieldId,
    })
    setSignatures((prev) => [...prev, newSignature])
  }, [reportId])

  const handleDeleteSignature = useCallback(async (signatureId: string) => {
    if (!reportId) return

    await signatureApi.delete(reportId, signatureId)
    setSignatures((prev) => prev.filter((s) => s.id !== signatureId))
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

  const isReadOnly = report?.status === 'completed' || report?.status === 'archived'

  return {
    reportId,
    navigate,
    report,
    isLoading,
    error: error as Error | null,
    tenantLogo,
    watermarkText,
    infoValues,
    setInfoValues,
    responses,
    setResponses,
    expandedSections,
    showComments,
    isInitialized,
    showDraftRecovery,
    photos,
    cameraOpen,
    setCameraOpen,
    cameraResponseId,
    isDownloading,
    signatures,
    showCertificateModal,
    setShowCertificateModal,
    isCompleting,
    autoSave,
    isReadOnly,
    progress,
    toggleSection,
    toggleComment,
    handleSave,
    handlePreFillAll,
    handleOpenCompleteModal,
    handleComplete,
    handleDownloadPdf,
    recoverDraft,
    dismissDraftRecovery,
    openCamera,
    handlePhotoCapture,
    handlePhotoDelete,
    getResponseId,
    handleAddSignature,
    handleDeleteSignature,
    completeMutation,
  }
}
