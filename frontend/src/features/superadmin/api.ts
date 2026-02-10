import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import type {
  TenantWithConfig,
  TenantFilters,
  CreateTenantWithConfig,
  UpdateTenantConfig,
  SuspendTenantRequest,
  AssignPlanRequest,
  TenantPlan,
  CreatePlanRequest,
  UpdatePlanRequest,
  TenantAuditLog,
  TenantUsage,
  PaginatedResponse,
} from './types'

// ── Tenant CRUD ──────────────────────────────────────────────────────

export function useSuperAdminTenants(filters: TenantFilters = {}) {
  return useQuery({
    queryKey: ['superadmin-tenants', filters],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<TenantWithConfig>>(
        '/superadmin/tenants',
        { params: filters }
      )
      return data
    },
  })
}

export function useSuperAdminTenantDetails(tenantId: string) {
  return useQuery({
    queryKey: ['superadmin-tenants', tenantId],
    queryFn: async () => {
      const { data } = await api.get<TenantWithConfig>(
        `/superadmin/tenants/${tenantId}`
      )
      return data
    },
    enabled: !!tenantId,
  })
}

export function useCreateTenantWithConfig() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreateTenantWithConfig) => {
      const { data } = await api.post<TenantWithConfig>(
        '/superadmin/tenants',
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
    },
  })
}

export function useUpdateTenantConfig(tenantId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: UpdateTenantConfig) => {
      const { data } = await api.put<TenantWithConfig>(
        `/superadmin/tenants/${tenantId}`,
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
    },
  })
}

// ── Tenant Status ────────────────────────────────────────────────────

export function useSuspendTenant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      tenantId,
      ...payload
    }: SuspendTenantRequest & { tenantId: string }) => {
      const { data } = await api.post<TenantWithConfig>(
        `/superadmin/tenants/${tenantId}/suspend`,
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
    },
  })
}

export function useActivateTenant() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (tenantId: string) => {
      const { data } = await api.post<TenantWithConfig>(
        `/superadmin/tenants/${tenantId}/activate`
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
    },
  })
}

// ── Plans ────────────────────────────────────────────────────────────

export function useTenantPlans() {
  return useQuery({
    queryKey: ['superadmin-plans'],
    queryFn: async () => {
      const { data } = await api.get<TenantPlan[]>('/superadmin/plans')
      return data
    },
  })
}

export function useCreatePlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreatePlanRequest) => {
      const { data } = await api.post<TenantPlan>(
        '/superadmin/plans',
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-plans'] })
    },
  })
}

export function useUpdatePlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }: UpdatePlanRequest) => {
      const { data } = await api.put<TenantPlan>(
        `/superadmin/plans/${id}`,
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-plans'] })
    },
  })
}

export function useAssignPlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      tenantId,
      ...payload
    }: AssignPlanRequest & { tenantId: string }) => {
      const { data } = await api.put<TenantWithConfig>(
        `/superadmin/tenants/${tenantId}/plan`,
        payload
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['superadmin-tenants'] })
      queryClient.invalidateQueries({ queryKey: ['superadmin-plans'] })
    },
  })
}

// ── Audit & Usage ────────────────────────────────────────────────────

export function useTenantAuditLog(tenantId: string, page = 1) {
  return useQuery({
    queryKey: ['superadmin-audit', tenantId, page],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<TenantAuditLog>>(
        `/superadmin/tenants/${tenantId}/audit`,
        { params: { page } }
      )
      return data
    },
    enabled: !!tenantId,
  })
}

export function useTenantUsage(tenantId: string) {
  return useQuery({
    queryKey: ['superadmin-usage', tenantId],
    queryFn: async () => {
      const { data } = await api.get<TenantUsage>(
        `/superadmin/tenants/${tenantId}/usage`
      )
      return data
    },
    enabled: !!tenantId,
  })
}
