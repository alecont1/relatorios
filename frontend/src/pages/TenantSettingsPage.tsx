import { Building2 } from 'lucide-react'
import { TenantSettingsForm } from '@/features/tenant/components'

export function TenantSettingsPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Building2 className="h-6 w-6 text-gray-600" />
        <h1 className="text-2xl font-bold text-gray-900">Configuracoes da Empresa</h1>
      </div>

      <p className="mb-6 text-sm text-gray-600">
        Configure a identidade visual, marca d'agua e informacoes de contato da sua empresa.
      </p>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <TenantSettingsForm />
      </div>
    </div>
  )
}
