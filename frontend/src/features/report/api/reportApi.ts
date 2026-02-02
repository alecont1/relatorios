import { api } from '@/lib/axios'

// --- Types ---

export interface InfoValue {
  id: string
  report_id: string
  info_field_id: string | null
  field_label: string
  field_type: string
  value: string | null
  created_at: string
}

export interface ChecklistResponse {
  id: string
  report_id: string
  section_id: string | null
  field_id: string | null
  section_name: string
  section_order: number
  field_label: string
  field_order: number
  field_type: string
  field_options: string | null
  response_value: string | null
  comment: string | null
  photos: Array<{ photo_id: string; url: string; caption?: string }>
  created_at: string
}

export interface Report {
  id: string
  tenant_id: string
  template_id: string
  project_id: string
  user_id: string
  title: string
  status: ReportStatus
  location: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  template_name?: string
}

export interface ReportDetail extends Report {
  template_snapshot: TemplateSnapshot
  info_values: InfoValue[]
  checklist_responses: ChecklistResponse[]
}

export interface TemplateSnapshot {
  id: string
  name: string
  code: string
  category: string
  version: number
  title: string | null
  reference_standards: string | null
  planning_requirements: string | null
  info_fields: SnapshotInfoField[]
  sections: SnapshotSection[]
  signature_fields: SnapshotSignatureField[]
}

export interface SnapshotInfoField {
  id: string
  label: string
  field_type: string
  placeholder: string | null
  required: boolean
  order: number
}

export interface SnapshotSection {
  id: string
  name: string
  order: number
  fields: SnapshotField[]
}

export interface SnapshotField {
  id: string
  label: string
  field_type: string
  options: string | null
  order: number
  photo_config: {
    required?: boolean
    min_count?: number
    max_count?: number
    require_gps?: boolean
    watermark?: boolean
  } | null
  comment_config: {
    enabled?: boolean
    required?: boolean
  } | null
}

export interface SnapshotSignatureField {
  id: string
  role_name: string
  required: boolean
  order: number
}

export type ReportStatus = 'draft' | 'in_progress' | 'completed' | 'archived'

export interface ReportListResponse {
  reports: Report[]
  total: number
}

export interface CreateReportData {
  template_id: string
  project_id: string
  title: string
  location?: string
}

export interface UpdateReportData {
  title?: string
  location?: string
  status?: ReportStatus
  info_values?: Array<{
    info_field_id?: string
    field_label: string
    field_type: string
    value?: string
  }>
  checklist_responses?: Array<{
    section_id?: string
    field_id?: string
    section_name: string
    section_order: number
    field_label: string
    field_order: number
    field_type: string
    field_options?: string
    response_value?: string
    comment?: string
    photos?: Array<{ photo_id: string; url: string; caption?: string }>
  }>
}

// --- API Functions ---

export const reportApi = {
  /**
   * List reports with optional filters
   */
  list: async (params?: {
    status?: ReportStatus
    template_id?: string
    skip?: number
    limit?: number
  }): Promise<ReportListResponse> => {
    const response = await api.get('/reports/', { params })
    return response.data
  },

  /**
   * Get a report by ID with all details
   */
  get: async (id: string): Promise<ReportDetail> => {
    const response = await api.get(`/reports/${id}`)
    return response.data
  },

  /**
   * Create a new report from a template
   */
  create: async (data: CreateReportData): Promise<ReportDetail> => {
    const response = await api.post('/reports/', data)
    return response.data
  },

  /**
   * Update a report (save draft)
   */
  update: async (id: string, data: UpdateReportData): Promise<ReportDetail> => {
    const response = await api.patch(`/reports/${id}`, data)
    return response.data
  },

  /**
   * Mark a report as completed
   */
  complete: async (id: string): Promise<ReportDetail> => {
    const response = await api.post(`/reports/${id}/complete`)
    return response.data
  },

  /**
   * Archive a completed report
   */
  archive: async (id: string): Promise<ReportDetail> => {
    const response = await api.post(`/reports/${id}/archive`)
    return response.data
  },

  /**
   * Download report as PDF
   */
  downloadPdf: async (id: string, filename?: string): Promise<void> => {
    const response = await api.get(`/reports/${id}/pdf`, {
      responseType: 'blob',
    })

    // Create blob URL and trigger download
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename || 'report.pdf'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  },
}
