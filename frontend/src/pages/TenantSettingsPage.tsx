import { useMemo } from 'react'
import { Building2, Eye } from 'lucide-react'
import { TenantSettingsForm } from '@/features/tenant/components'
import { PdfCoverPreview } from '@/features/template/components/PdfCoverPreview'
import { useTenantBranding } from '@/features/tenant/api'
import { getLogoUrl } from '@/features/tenant/types'
import type { Template, InfoField, SignatureField } from '@/features/template/api/templateApi'

// Mock data for preview (same as onboarding)
const MOCK_TEMPLATE: Template = {
  id: 'preview',
  tenant_id: '',
  name: 'Relatorio Exemplo',
  code: 'REL-001',
  category: 'inspecao',
  status: 'active',
  version: 1,
  title: null,
  reference_standards: 'NBR 5410:2004',
  planning_requirements: null,
  pdf_layout_id: null,
  created_at: '',
  updated_at: '',
}

const MOCK_INFO_FIELDS: InfoField[] = [
  { id: '1', template_id: '', label: 'Cliente', field_type: 'text', placeholder: 'Nome do cliente', required: true, order: 0 },
  { id: '2', template_id: '', label: 'Local', field_type: 'text', placeholder: 'Local da inspecao', required: true, order: 1 },
  { id: '3', template_id: '', label: 'Data', field_type: 'date', placeholder: '', required: true, order: 2 },
]

const MOCK_SIGNATURE_FIELDS: SignatureField[] = [
  { id: '1', template_id: '', role_name: 'Tecnico Responsavel', required: true, order: 0 },
  { id: '2', template_id: '', role_name: 'Cliente', required: true, order: 1 },
]

export function TenantSettingsPage() {
  const { data: branding } = useTenantBranding()

  // Live branding for preview - updates when branding changes (after save)
  const brandingOverride = useMemo(() => ({
    logoUrl: getLogoUrl(branding?.logo_primary_key) ?? undefined,
    companyName: branding?.name ?? 'Empresa',
    primaryColor: branding?.brand_color_primary ?? '#2563eb',
  }), [branding?.logo_primary_key, branding?.name, branding?.brand_color_primary])

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Building2 className="h-6 w-6 text-gray-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuracoes da Empresa</h1>
          <p className="text-sm text-gray-600">
            Configure a identidade visual, marca d'agua e informacoes de contato da sua empresa.
          </p>
        </div>
      </div>

      <div className="flex gap-6">
        {/* Form - main content */}
        <div className="flex-1 rounded-lg border border-gray-200 bg-white p-6">
          <TenantSettingsForm />
        </div>

        {/* PDF Preview - sticky sidebar (hidden on small screens) */}
        <div className="hidden lg:block w-[320px] shrink-0">
          <div className="sticky top-24 space-y-3">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Preview da Capa do PDF</span>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
            </div>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 flex justify-center">
              <PdfCoverPreview
                template={MOCK_TEMPLATE}
                infoFields={MOCK_INFO_FIELDS}
                signatureFields={MOCK_SIGNATURE_FIELDS}
                brandingOverride={brandingOverride}
              />
            </div>
            <p className="text-xs text-gray-400 text-center">
              O preview atualiza apos salvar as alteracoes
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
