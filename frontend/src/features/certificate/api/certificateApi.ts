import { api } from '@/lib/axios'

// --- Types ---

export interface Certificate {
  id: string
  tenant_id: string
  equipment_name: string
  certificate_number: string
  manufacturer: string | null
  model: string | null
  serial_number: string | null
  laboratory: string | null
  calibration_date: string // "YYYY-MM-DD"
  expiry_date: string // "YYYY-MM-DD"
  file_key: string | null
  status: 'valid' | 'expiring' | 'expired'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CertificateCreate {
  equipment_name: string
  certificate_number: string
  manufacturer?: string
  model?: string
  serial_number?: string
  laboratory?: string
  calibration_date: string
  expiry_date: string
  status?: 'valid' | 'expiring' | 'expired'
}

export interface CertificateUpdate {
  equipment_name?: string
  certificate_number?: string
  manufacturer?: string
  model?: string
  serial_number?: string
  laboratory?: string
  calibration_date?: string
  expiry_date?: string
  status?: 'valid' | 'expiring' | 'expired'
}

export interface CertificateListResponse {
  certificates: Certificate[]
  total: number
}

export interface ReportCertificateLink {
  certificate_ids: string[]
}

// --- API Functions ---

export const certificateApi = {
  /**
   * List certificates with optional filters
   */
  list: async (params?: {
    search?: string
    status?: string
    active_only?: boolean
    skip?: number
    limit?: number
  }): Promise<CertificateListResponse> => {
    const response = await api.get('/certificates/', { params })
    return response.data
  },

  /**
   * Get a certificate by ID
   */
  get: async (id: string): Promise<Certificate> => {
    const response = await api.get(`/certificates/${id}`)
    return response.data
  },

  /**
   * Create a new certificate
   */
  create: async (data: CertificateCreate): Promise<Certificate> => {
    const response = await api.post('/certificates/', data)
    return response.data
  },

  /**
   * Update a certificate
   */
  update: async (id: string, data: CertificateUpdate): Promise<Certificate> => {
    const response = await api.patch(`/certificates/${id}`, data)
    return response.data
  },

  /**
   * Soft delete a certificate
   */
  delete: async (id: string): Promise<void> => {
    await api.delete(`/certificates/${id}`)
  },

  /**
   * Upload a PDF file for a certificate
   */
  uploadFile: async (id: string, file: File): Promise<Certificate> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`/certificates/${id}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  /**
   * List certificates linked to a report
   */
  listForReport: async (reportId: string): Promise<CertificateListResponse> => {
    const response = await api.get(`/reports/${reportId}/certificates/`)
    return response.data
  },

  /**
   * Link certificates to a report
   */
  linkToReport: async (reportId: string, certificateIds: string[]): Promise<void> => {
    await api.post(`/reports/${reportId}/certificates/link`, {
      certificate_ids: certificateIds,
    })
  },

  /**
   * Unlink certificates from a report
   */
  unlinkFromReport: async (reportId: string, certificateIds: string[]): Promise<void> => {
    await api.post(`/reports/${reportId}/certificates/unlink`, {
      certificate_ids: certificateIds,
    })
  },
}
