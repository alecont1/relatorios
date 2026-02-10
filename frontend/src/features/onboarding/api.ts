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
