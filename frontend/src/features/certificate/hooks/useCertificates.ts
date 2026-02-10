import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  certificateApi,
  type CertificateCreate,
  type CertificateUpdate,
} from '../api/certificateApi'

/**
 * Query key factory for certificates
 */
const certificateKeys = {
  all: ['certificates'] as const,
  lists: () => [...certificateKeys.all, 'list'] as const,
  list: (params?: { search?: string; status?: string }) =>
    [...certificateKeys.lists(), params] as const,
  details: () => [...certificateKeys.all, 'detail'] as const,
  detail: (id: string) => [...certificateKeys.details(), id] as const,
  forReport: (reportId: string) =>
    [...certificateKeys.all, 'report', reportId] as const,
}

/**
 * Hook to list certificates with optional filters
 */
export function useCertificates(params?: {
  search?: string
  status?: string
  active_only?: boolean
  skip?: number
  limit?: number
}) {
  return useQuery({
    queryKey: certificateKeys.list({
      search: params?.search,
      status: params?.status,
    }),
    queryFn: () => certificateApi.list(params),
  })
}

/**
 * Hook to get a single certificate by ID
 */
export function useCertificate(id: string | undefined) {
  return useQuery({
    queryKey: certificateKeys.detail(id!),
    queryFn: () => certificateApi.get(id!),
    enabled: !!id,
  })
}

/**
 * Hook to create a certificate
 */
export function useCreateCertificate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CertificateCreate) => certificateApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.lists() })
    },
  })
}

/**
 * Hook to update a certificate
 */
export function useUpdateCertificate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CertificateUpdate }) =>
      certificateApi.update(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.lists() })
      queryClient.invalidateQueries({
        queryKey: certificateKeys.detail(variables.id),
      })
    },
  })
}

/**
 * Hook to delete a certificate (soft delete)
 */
export function useDeleteCertificate() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => certificateApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.lists() })
    },
  })
}

/**
 * Hook to upload a PDF file for a certificate
 */
export function useUploadCertificateFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) =>
      certificateApi.uploadFile(id, file),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: certificateKeys.lists() })
      queryClient.invalidateQueries({
        queryKey: certificateKeys.detail(variables.id),
      })
    },
  })
}

/**
 * Hook to link certificates to a report
 */
export function useLinkCertificates(reportId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (certificateIds: string[]) =>
      certificateApi.linkToReport(reportId, certificateIds),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: certificateKeys.forReport(reportId),
      })
    },
  })
}

/**
 * Hook to unlink certificates from a report
 */
export function useUnlinkCertificates(reportId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (certificateIds: string[]) =>
      certificateApi.unlinkFromReport(reportId, certificateIds),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: certificateKeys.forReport(reportId),
      })
    },
  })
}
