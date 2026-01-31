import { Settings } from 'lucide-react'
import { TenantSettingsForm } from '@/features/tenant/components'

export function TenantSettingsPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Settings className="h-6 w-6 text-gray-600" />
        <h1 className="text-2xl font-bold text-gray-900">Configuracoes do Tenant</h1>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <TenantSettingsForm />
      </div>
    </div>
  )
}
