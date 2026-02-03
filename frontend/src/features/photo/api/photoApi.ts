/**
 * Photo API client for uploading and managing photos.
 */
import api from '@/lib/axios'

export interface GPSCoordinates {
  latitude: number
  longitude: number
  accuracy?: number
}

export interface PhotoMetadata {
  id: string
  url: string
  thumbnail_url?: string
  original_filename?: string
  size_bytes?: number
  width?: number
  height?: number
  captured_at: string
  gps?: GPSCoordinates
  address?: string
  watermarked: boolean
}

export interface PhotoUploadData {
  response_id: string
  file: Blob
  captured_at?: Date
  latitude?: number
  longitude?: number
  gps_accuracy?: number
  address?: string
}

export interface PhotoListItem {
  response_id: string
  field_label: string
  photos: PhotoMetadata[]
  max_photos?: number
  required: boolean
}

export const photoApi = {
  /**
   * Upload a photo to a checklist response.
   */
  async upload(reportId: string, data: PhotoUploadData): Promise<PhotoMetadata> {
    const formData = new FormData()
    formData.append('response_id', data.response_id)
    formData.append('file', data.file, 'photo.jpg')

    if (data.captured_at) {
      formData.append('captured_at', data.captured_at.toISOString())
    }
    if (data.latitude !== undefined) {
      formData.append('latitude', String(data.latitude))
    }
    if (data.longitude !== undefined) {
      formData.append('longitude', String(data.longitude))
    }
    if (data.gps_accuracy !== undefined) {
      formData.append('gps_accuracy', String(data.gps_accuracy))
    }
    if (data.address) {
      formData.append('address', data.address)
    }

    const response = await api.post<{ photo: PhotoMetadata }>(
      `/reports/${reportId}/photos`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data.photo
  },

  /**
   * Delete a photo.
   */
  async delete(reportId: string, photoId: string): Promise<void> {
    await api.delete(`/reports/${reportId}/photos/${photoId}`)
  },

  /**
   * List all photos for a report.
   */
  async list(reportId: string): Promise<PhotoListItem[]> {
    const response = await api.get<PhotoListItem[]>(
      `/reports/${reportId}/photos`
    )
    return response.data
  },
}
