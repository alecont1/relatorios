import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import type {
  OnboardingStatus,
  StepKey,
  StepUpdateRequest,
  StepUpdateResponse,
  CloneDemoTemplateResponse,
} from './types'

/**
 * Fetch the current tenant's onboarding status.
 */
export function useOnboardingStatus(enabled?: boolean) {
  return useQuery({
    queryKey: ['onboarding-status'],
    queryFn: async () => {
      const { data } = await api.get<OnboardingStatus>('/onboarding/status')
      return data
    },
    staleTime: 30_000,
    enabled,
  })
}

/**
 * Mark an onboarding step as completed or skipped.
 */
export function useUpdateStep() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ key, action }: { key: StepKey; action: StepUpdateRequest['action'] }) => {
      const { data } = await api.put<StepUpdateResponse>(
        `/onboarding/step/${key}`,
        { action } satisfies StepUpdateRequest
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] })
    },
  })
}

/**
 * Clone the demo template for the current tenant.
 */
export function useCloneDemoTemplate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post<CloneDemoTemplateResponse>(
        '/onboarding/clone-demo-template'
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['onboarding-status'] })
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })
}

/**
 * Fetch a report's PDF as a blob and return an object URL for iframe display.
 * Cleans up the blob URL on unmount or when reportId changes.
 */
export function useReportPdfBlob(reportId: string | null) {
  const [blobUrl, setBlobUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reportId) {
      setBlobUrl(null)
      return
    }

    let cancelled = false
    let url: string | null = null

    const fetchPdf = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await api.get(`/reports/${reportId}/pdf`, {
          responseType: 'blob',
        })
        if (cancelled) return
        const blob = new Blob([response.data], { type: 'application/pdf' })
        url = window.URL.createObjectURL(blob)
        setBlobUrl(url)
      } catch (err: unknown) {
        if (cancelled) return
        const axiosError = err as { response?: { status?: number } }
        if (axiosError.response?.status === 404) {
          setError('PDF nao disponivel para este relatorio')
        } else {
          setError('Erro ao carregar PDF')
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    fetchPdf()

    return () => {
      cancelled = true
      if (url) {
        window.URL.revokeObjectURL(url)
      }
    }
  }, [reportId])

  // Helper to trigger download
  const downloadPdf = () => {
    if (!blobUrl) return
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `relatorio-${reportId}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return { blobUrl, isLoading, error, downloadPdf }
}
