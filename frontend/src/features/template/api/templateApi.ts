import api from '@/lib/axios'

// ============================================================================
// Checklist Field Types (within sections)
// ============================================================================

export interface TemplateField {
  id?: string
  label: string
  field_type: 'dropdown' | 'text'
  options: string[] | null
  order: number
  photo_config?: PhotoConfig | null
  comment_config?: CommentConfig | null
}

// ============================================================================
// Info Field Types (project metadata)
// ============================================================================

export interface InfoField {
  id: string
  template_id: string
  label: string
  field_type: 'text' | 'date' | 'select'
  options: string[] | null
  required: boolean
  order: number
  created_at: string
  updated_at: string
}

export interface InfoFieldCreate {
  label: string
  field_type: 'text' | 'date' | 'select'
  options?: string[]
  required: boolean
}

export interface InfoFieldUpdate {
  label?: string
  field_type?: 'text' | 'date' | 'select'
  options?: string[]
  required?: boolean
}

export interface InfoFieldListResponse {
  info_fields: InfoField[]
  total: number
}

// ============================================================================
// Signature Field Types
// ============================================================================

export interface SignatureField {
  id: string
  template_id: string
  role_name: string
  required: boolean
  order: number
  created_at: string
  updated_at: string
}

export interface SignatureFieldCreate {
  role_name: string
  required: boolean
}

export interface SignatureFieldUpdate {
  role_name?: string
  required?: boolean
}

export interface SignatureFieldListResponse {
  signature_fields: SignatureField[]
  total: number
}

// ============================================================================
// Field Configuration Types (photo/comment settings)
// ============================================================================

export interface PhotoConfig {
  required: boolean
  min_count: number
  max_count: number
  require_gps: boolean
  watermark: boolean
}

export interface CommentConfig {
  enabled: boolean
  required: boolean
}

export interface FieldConfigUpdate {
  photo_config?: PhotoConfig
  comment_config?: CommentConfig
}

export interface FieldConfigResponse {
  id: string
  label: string
  field_type: string
  photo_config: PhotoConfig | null
  comment_config: CommentConfig | null
}

export interface TemplateSection {
  id?: string
  name: string
  order: number
  fields: TemplateField[]
}

export interface Template {
  id: string
  tenant_id: string
  name: string
  code: string
  category: string
  version: number
  title: string | null
  reference_standards: string | null
  planning_requirements: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  sections?: TemplateSection[]
}

export interface TemplateListItem {
  id: string
  name: string
  code: string
  category: string
  version: number
  is_active: boolean
  created_at: string
}

export interface TemplateListResponse {
  templates: TemplateListItem[]
  total: number
}

export interface ExcelParseResponse {
  valid: boolean
  sections?: TemplateSection[]
  errors?: string[]
  summary?: {
    section_count: number
    field_count: number
  }
}

export interface TemplateCreateData {
  name: string
  category: 'Commissioning' | 'Inspection' | 'Maintenance' | 'Testing'
  sections: TemplateSection[]
  title?: string
  reference_standards?: string
  planning_requirements?: string
}

export const templateApi = {
  list: async (params: { search?: string; status?: string; skip?: number; limit?: number }) => {
    const response = await api.get<TemplateListResponse>('/templates', { params })
    return response.data
  },

  get: async (id: string) => {
    const response = await api.get<Template>(`/templates/${id}`)
    return response.data
  },

  parse: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post<ExcelParseResponse>('/templates/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  create: async (data: TemplateCreateData) => {
    const response = await api.post<Template>('/templates', data)
    return response.data
  },

  update: async (id: string, data: Partial<TemplateCreateData> & { is_active?: boolean }) => {
    const response = await api.patch<Template>(`/templates/${id}`, data)
    return response.data
  },

  // ============================================================================
  // Info Fields API
  // ============================================================================

  getInfoFields: async (templateId: string) => {
    const response = await api.get<InfoFieldListResponse>(`/templates/${templateId}/info-fields`)
    return response.data
  },

  createInfoField: async (templateId: string, data: InfoFieldCreate) => {
    const response = await api.post<InfoField>(`/templates/${templateId}/info-fields`, data)
    return response.data
  },

  updateInfoField: async (templateId: string, fieldId: string, data: InfoFieldUpdate) => {
    const response = await api.patch<InfoField>(`/templates/${templateId}/info-fields/${fieldId}`, data)
    return response.data
  },

  deleteInfoField: async (templateId: string, fieldId: string) => {
    await api.delete(`/templates/${templateId}/info-fields/${fieldId}`)
  },

  reorderInfoFields: async (templateId: string, fieldIds: string[]) => {
    const response = await api.put<InfoFieldListResponse>(`/templates/${templateId}/info-fields/reorder`, { field_ids: fieldIds })
    return response.data
  },

  // ============================================================================
  // Signature Fields API
  // ============================================================================

  getSignatureFields: async (templateId: string) => {
    const response = await api.get<SignatureFieldListResponse>(`/templates/${templateId}/signature-fields`)
    return response.data
  },

  createSignatureField: async (templateId: string, data: SignatureFieldCreate) => {
    const response = await api.post<SignatureField>(`/templates/${templateId}/signature-fields`, data)
    return response.data
  },

  updateSignatureField: async (templateId: string, fieldId: string, data: SignatureFieldUpdate) => {
    const response = await api.patch<SignatureField>(`/templates/${templateId}/signature-fields/${fieldId}`, data)
    return response.data
  },

  deleteSignatureField: async (templateId: string, fieldId: string) => {
    await api.delete(`/templates/${templateId}/signature-fields/${fieldId}`)
  },

  reorderSignatureFields: async (templateId: string, fieldIds: string[]) => {
    const response = await api.put<SignatureFieldListResponse>(`/templates/${templateId}/signature-fields/reorder`, { field_ids: fieldIds })
    return response.data
  },

  // ============================================================================
  // Field Configuration API
  // ============================================================================

  getFieldConfig: async (fieldId: string) => {
    const response = await api.get<FieldConfigResponse>(`/templates/fields/${fieldId}/config`)
    return response.data
  },

  updateFieldConfig: async (fieldId: string, data: FieldConfigUpdate) => {
    const response = await api.patch<FieldConfigResponse>(`/templates/fields/${fieldId}/config`, data)
    return response.data
  },
}
