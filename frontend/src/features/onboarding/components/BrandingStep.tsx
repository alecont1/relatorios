import { useEffect } from 'react'
import { TenantSettingsForm } from '@/features/tenant/components/TenantSettingsForm'
import { useUpdateBranding } from '@/features/tenant/api'

interface BrandingStepProps {
  onComplete: () => void
}

export function BrandingStep({ onComplete }: BrandingStepProps) {
  const updateBranding = useUpdateBranding()

  useEffect(() => {
    if (updateBranding.isSuccess) {
      onComplete()
    }
  }, [updateBranding.isSuccess, onComplete])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">
          Identidade Visual
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Configure logos, cores e contato da sua empresa
        </p>
      </div>

      <div className="onboarding-branding-logos onboarding-branding-colors onboarding-branding-contact">
        <TenantSettingsForm />
      </div>
    </div>
  )
}
