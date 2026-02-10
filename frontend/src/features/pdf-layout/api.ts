import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import type { PdfLayoutListResponse } from './types'

export function usePdfLayouts() {
  return useQuery({
    queryKey: ['pdf-layouts'],
    queryFn: async () => {
      const { data } = await api.get<PdfLayoutListResponse>('/pdf-layouts')
      return data
    },
  })
}
