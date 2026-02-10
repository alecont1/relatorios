import { useState, useEffect, useRef, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { useTenantBranding, useUpdateBranding } from '@/features/tenant/api'
import { useTenantStore } from '@/features/tenant/store'
import { ColorPicker } from '@/features/tenant/components/ColorPicker'
import { LogoUploader } from '@/features/tenant/components/LogoUploader'
import { PdfCoverPreview } from '@/features/template/components/PdfCoverPreview'
import { getLogoUrl } from '@/features/tenant/types'
import type { UpdateBrandingRequest } from '@/features/tenant/types'
import type { Template, InfoField, SignatureField } from '@/features/template/api/templateApi'

interface BrandingStepProps {
  onComplete: () => void
}

// Mock template for PDF preview during onboarding
const MOCK_TEMPLATE: Template = {
  id: 'onboarding-preview',
  tenant_id: '',
  name: 'CPQ11 - Comissionamento de Quadros Eletricos',
  code: 'CPQ11-DEMO',
  category: 'Commissioning',
  version: 1,
  title: 'Protocolo de Comissionamento',
  reference_standards: 'NBR IEC 61439-1',
  planning_requirements: null,
  is_active: true,
  created_at: '',
  updated_at: '',
  sections: [
    {
      id: 'mock-s1',
      template_id: 'onboarding-preview',
      name: '1. Verificacao Visual e Mecanica',
      order: 1,
      fields: [
        { id: 'f1', section_id: 'mock-s1', label: 'Integridade fisica do involucro', field_type: 'dropdown', options: 'Conforme,Nao Conforme,N/A', order: 1, photo_config: { required: false, min_count: 0, max_count: 5 }, comment_config: { enabled: true, required: false } },
        { id: 'f2', section_id: 'mock-s1', label: 'Fixacao e aterramento', field_type: 'dropdown', options: 'Conforme,Nao Conforme,N/A', order: 2, photo_config: null, comment_config: { enabled: true, required: false } },
        { id: 'f3', section_id: 'mock-s1', label: 'Identificacao dos circuitos', field_type: 'dropdown', options: 'Conforme,Nao Conforme,N/A', order: 3, photo_config: { required: false, min_count: 0, max_count: 3 }, comment_config: { enabled: true, required: false } },
        { id: 'f4', section_id: 'mock-s1', label: 'Grau de protecao IP', field_type: 'dropdown', options: 'Conforme,Nao Conforme,N/A', order: 4, photo_config: null, comment_config: { enabled: true, required: false } },
        { id: 'f5', section_id: 'mock-s1', label: 'Distancias de seguranca', field_type: 'dropdown', options: 'Conforme,Nao Conforme,N/A', order: 5, photo_config: null, comment_config: { enabled: true, required: false } },
      ],
    },
  ],
}

const MOCK_INFO_FIELDS: InfoField[] = [
  { id: 'i1', template_id: 'onboarding-preview', label: 'Local', field_type: 'text', order: 1, is_required: false },
  { id: 'i2', template_id: 'onboarding-preview', label: 'Responsavel', field_type: 'text', order: 2, is_required: false },
  { id: 'i3', template_id: 'onboarding-preview', label: 'Data', field_type: 'text', order: 3, is_required: false },
]

const MOCK_SIGNATURE_FIELDS: SignatureField[] = [
  { id: 's1', template_id: 'onboarding-preview', role_name: 'Tecnico', order: 1, is_required: true },
  { id: 's2', template_id: 'onboarding-preview', role_name: 'Supervisor', order: 2, is_required: false },
]

export function BrandingStep({ onComplete }: BrandingStepProps) {
  const { data: branding, isLoading, refetch } = useTenantBranding()
  const updateBranding = useUpdateBranding()
  const { setBranding } = useTenantStore()
  const completedRef = useRef(false)

  const [logoPreviewUrl, setLogoPreviewUrl] = useState<string | null>(null)

  const { register, handleSubmit, setValue, watch } = useForm<UpdateBrandingRequest>()

  // Sync branding to store when loaded
  useEffect(() => {
    if (branding) {
      setBranding(branding)
      // Set initial logo preview from saved branding
      const savedLogoUrl = getLogoUrl(branding.logo_primary_key)
      if (savedLogoUrl && !logoPreviewUrl) {
        setLogoPreviewUrl(savedLogoUrl)
      }
    }
  }, [branding, setBranding])

  // Set form values when branding loads
  useEffect(() => {
    if (branding) {
      setValue('brand_color_primary', branding.brand_color_primary)
      setValue('brand_color_secondary', branding.brand_color_secondary)
      setValue('brand_color_accent', branding.brand_color_accent)
      setValue('contact_address', branding.contact_address)
      setValue('contact_phone', branding.contact_phone)
      setValue('contact_email', branding.contact_email)
      setValue('contact_website', branding.contact_website)
      setValue('watermark_text', branding.watermark_text)
    }
  }, [branding, setValue])

  // Auto-complete step on successful save
  if (updateBranding.isSuccess && !completedRef.current) {
    completedRef.current = true
    onComplete()
  }

  const onSubmit = async (data: UpdateBrandingRequest) => {
    await updateBranding.mutateAsync(data)
  }

  // Watch form values for live preview
  const watchedPrimaryColor = watch('brand_color_primary')
  const watchedCompanyName = branding?.name ?? 'Sua Empresa'

  // Branding override for live preview
  const brandingOverride = useMemo(() => ({
    logoUrl: logoPreviewUrl ?? undefined,
    companyName: watchedCompanyName,
    primaryColor: watchedPrimaryColor ?? '#2563eb',
  }), [logoPreviewUrl, watchedCompanyName, watchedPrimaryColor])

  if (isLoading) {
    return <div className="text-gray-500">Carregando...</div>
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Sua Marca</h2>
        <p className="mt-1 text-sm text-gray-500">
          Personalize a identidade visual e veja o resultado no preview do PDF ao lado
        </p>
      </div>

      <div className="flex gap-8">
        {/* Form (left side) */}
        <form onSubmit={handleSubmit(onSubmit)} className="flex-1 min-w-0 space-y-6">
          {/* Logos */}
          <section className="onboarding-branding-logos">
            <h3 className="mb-3 text-sm font-semibold text-gray-800 uppercase tracking-wide">Logos</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <LogoUploader
                label="Logo Primaria"
                logoType="primary"
                currentKey={branding?.logo_primary_key ?? null}
                onUploadComplete={refetch}
                onPreviewChange={(url) => setLogoPreviewUrl(url)}
              />
              <LogoUploader
                label="Logo Secundaria"
                logoType="secondary"
                currentKey={branding?.logo_secondary_key ?? null}
                onUploadComplete={refetch}
              />
            </div>
          </section>

          {/* Colors */}
          <section className="onboarding-branding-colors">
            <h3 className="mb-3 text-sm font-semibold text-gray-800 uppercase tracking-wide">Cores da Marca</h3>
            <div className="grid gap-4 md:grid-cols-3">
              <ColorPicker
                label="Cor Primaria"
                value={watch('brand_color_primary') ?? null}
                onChange={(color) => setValue('brand_color_primary', color)}
              />
              <ColorPicker
                label="Cor Secundaria"
                value={watch('brand_color_secondary') ?? null}
                onChange={(color) => setValue('brand_color_secondary', color)}
              />
              <ColorPicker
                label="Cor de Destaque"
                value={watch('brand_color_accent') ?? null}
                onChange={(color) => setValue('brand_color_accent', color)}
              />
            </div>
          </section>

          {/* Contact Info */}
          <section className="onboarding-branding-contact">
            <h3 className="mb-3 text-sm font-semibold text-gray-800 uppercase tracking-wide">Contato</h3>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">Endereco</label>
                <input
                  {...register('contact_address')}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="Rua, numero, cidade"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Telefone</label>
                <input
                  {...register('contact_phone')}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="(11) 99999-9999"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  {...register('contact_email')}
                  type="email"
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="contato@empresa.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Website</label>
                <input
                  {...register('contact_website')}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                  placeholder="https://www.empresa.com"
                />
              </div>
            </div>
          </section>

          {/* Watermark */}
          <section>
            <h3 className="mb-3 text-sm font-semibold text-gray-800 uppercase tracking-wide">Marca d'Agua</h3>
            <div>
              <input
                {...register('watermark_text')}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
                placeholder="Ex: CONFIDENCIAL - Nome da Empresa"
                maxLength={255}
              />
              <p className="mt-1 text-xs text-gray-400">
                Texto aplicado como marca d'agua nas fotos dos relatorios
              </p>
            </div>
          </section>

          {/* Submit */}
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={updateBranding.isPending}
              className="rounded-lg bg-green-600 px-6 py-2.5 text-white font-medium hover:bg-green-700 disabled:opacity-50"
            >
              {updateBranding.isPending ? 'Salvando...' : 'Salvar Configuracao'}
            </button>
            {updateBranding.isSuccess && (
              <span className="text-sm text-green-600">Salvo com sucesso!</span>
            )}
          </div>
        </form>

        {/* PDF Preview (right side) */}
        <div className="w-[520px] flex-shrink-0 hidden lg:block">
          <div className="sticky top-6">
            <div className="mb-3 flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Preview ao Vivo
              </span>
            </div>
            <PdfCoverPreview
              template={MOCK_TEMPLATE}
              infoFields={MOCK_INFO_FIELDS}
              signatureFields={MOCK_SIGNATURE_FIELDS}
              brandingOverride={brandingOverride}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
