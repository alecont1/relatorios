import api from '@/lib/axios'

export interface TemplateField {
  id?: string
  label: string
  field_type: 'dropdown' | 'text'
  options: string[] | null
  order: number
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
}
