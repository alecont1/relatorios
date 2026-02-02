import { api } from '@/lib/axios'

// --- Types ---

export interface SignatureData {
  id: string
  role_name: string
  signer_name: string | null
  url: string
  signed_at: string
  signature_field_id: string | null
  created_at: string
}

export interface SignatureListResponse {
  signatures: SignatureData[]
  total: number
}

export interface SignatureField {
  id: string
  role_name: string
  required: boolean
  order: number
}

// --- API Functions ---

export const signatureApi = {
  /**
   * List all signatures for a report
   */
  list: async (reportId: string): Promise<SignatureListResponse> => {
    const response = await api.get(`/reports/${reportId}/signatures`)
    return response.data
  },

  /**
   * Upload a signature
   */
  upload: async (
    reportId: string,
    data: {
      role_name: string
      file: Blob
      signer_name?: string
      signature_field_id?: string
    }
  ): Promise<SignatureData> => {
    const formData = new FormData()
    formData.append('role_name', data.role_name)
    formData.append('file', data.file, `${data.role_name}.png`)

    if (data.signer_name) {
      formData.append('signer_name', data.signer_name)
    }
    if (data.signature_field_id) {
      formData.append('signature_field_id', data.signature_field_id)
    }

    const response = await api.post(`/reports/${reportId}/signatures`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Delete a signature
   */
  delete: async (reportId: string, signatureId: string): Promise<void> => {
    await api.delete(`/reports/${reportId}/signatures/${signatureId}`)
  },
}
