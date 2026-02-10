import { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/features/auth'
import { useOnboardingStatus } from '../api'

export function useOnboardingGuard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const isTenantAdmin = user?.role === 'tenant_admin'
  const { data: status, isLoading } = useOnboardingStatus(isTenantAdmin)

  const isOnboardingIncomplete = isTenantAdmin && status ? !status.is_completed : false

  useEffect(() => {
    if (
      !isLoading &&
      isOnboardingIncomplete &&
      !location.pathname.startsWith('/onboarding')
    ) {
      navigate('/onboarding', { replace: true })
    }
  }, [isLoading, isOnboardingIncomplete, location.pathname, navigate])

  return { isOnboardingIncomplete, isLoading }
}
