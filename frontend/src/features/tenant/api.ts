import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import type {
  Tenant,
  TenantsListResponse,
  CreateTenantRequest,
  UpdateTenantRequest,
  UpdateBrandingRequest,
  LogoUploadUrlRequest,
  LogoUploadUrlResponse,
  LogoConfirmRequest,
} from './types'

// Superadmin: Tenant CRUD
export function useTenants(includeInactive = false) {
  return useQuery({
    queryKey: ['tenants', { includeInactive }],
    queryFn: async () => {
      const { data } = await api.get<TenantsListResponse>('/tenants', {
        params: { include_inactive: includeInactive },
      })
      return data
    },
  })
}

export function useCreateTenant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (tenant: CreateTenantRequest) => {
      const { data } = await api.post<Tenant>('/tenants', tenant)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] })
    },
  })
}

export function useUpdateTenant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...data }: UpdateTenantRequest & { id: string }) => {
      const { data: result } = await api.patch<Tenant>(`/tenants/${id}`, data)
      return result
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] })
    },
  })
}

// Admin: Tenant Settings
export function useTenantBranding() {
  return useQuery({
    queryKey: ['tenant-branding'],
    queryFn: async () => {
      const { data } = await api.get<Tenant>('/tenant-settings/branding')
      return data
    },
  })
}

export function useUpdateBranding() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (branding: UpdateBrandingRequest) => {
      const { data } = await api.patch<Tenant>('/tenant-settings/branding', branding)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant-branding'] })
    },
  })
}

export function useLogoUploadUrl() {
  return useMutation({
    mutationFn: async (request: LogoUploadUrlRequest) => {
      const { data } = await api.post<LogoUploadUrlResponse>(
        '/tenant-settings/logo/upload-url',
        request
      )
      return data
    },
  })
}

export function useLogoConfirm() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (request: LogoConfirmRequest) => {
      const { data } = await api.post<Tenant>('/tenant-settings/logo/confirm', request)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant-branding'] })
    },
  })
}
