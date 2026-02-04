import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/axios'
import { useTenantStore } from '../store'
import { useAuthStore } from '@/features/auth'
import type { Tenant } from '../types'

/**
 * Hook to automatically load tenant branding when user is authenticated.
 * Should be called once at the app root level.
 */
export function useBrandingLoader() {
  const { isAuthenticated, user } = useAuthStore()
  const { setBranding, clearBranding } = useTenantStore()

  // Only fetch when authenticated and user has a tenant
  const { data: branding } = useQuery({
    queryKey: ['tenant-branding'],
    queryFn: async () => {
      const { data } = await api.get<Tenant>('/tenant-settings/branding')
      return data
    },
    enabled: isAuthenticated && !!user,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Update store when branding loads
  useEffect(() => {
    if (branding) {
      setBranding(branding)
    }
  }, [branding, setBranding])

  // Clear branding when logged out
  useEffect(() => {
    if (!isAuthenticated) {
      clearBranding()
    }
  }, [isAuthenticated, clearBranding])

  return { isLoaded: !!branding }
}
