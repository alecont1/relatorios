import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useTenantBranding, useUpdateBranding } from '../api'
import { useTenantStore } from '../store'
import { ColorPicker } from './ColorPicker'
import { LogoUploader } from './LogoUploader'
import { WatermarkConfigPanel } from './WatermarkConfigPanel'
import type { UpdateBrandingRequest } from '../types'

export function TenantSettingsForm() {
  const { data: branding, isLoading, refetch } = useTenantBranding()
  const updateBranding = useUpdateBranding()
  const { setBranding } = useTenantStore()

  const { register, handleSubmit, setValue, watch } = useForm<UpdateBrandingRequest>()

  // Sync branding to store when loaded
  useEffect(() => {
    if (branding) {
      setBranding(branding)
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

  const onSubmit = async (data: UpdateBrandingRequest) => {
    await updateBranding.mutateAsync(data)
  }

  if (isLoading) {
    return <div className="text-gray-500">Carregando...</div>
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Logos */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Logos</h2>
        <div className="grid gap-6 md:grid-cols-2">
          <LogoUploader
            label="Logo Primaria"
            logoType="primary"
            currentKey={branding?.logo_primary_key ?? null}
            onUploadComplete={refetch}
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
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Cores da Marca</h2>
        <div className="grid gap-6 md:grid-cols-3">
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

      {/* Watermark */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Marca d'Agua</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700">Texto da Marca d'Agua</label>
          <input
            {...register('watermark_text')}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Ex: CONFIDENCIAL - Nome da Empresa"
            maxLength={255}
          />
          <p className="mt-1 text-xs text-gray-500">
            Este texto sera aplicado como marca d'agua nos relatorios e fotos gerados.
          </p>
        </div>

        {/* Watermark field toggles */}
        <div className="mt-6">
          <WatermarkConfigPanel
            currentConfig={branding?.watermark_config ?? null}
            onSaved={refetch}
          />
        </div>
      </section>

      {/* Contact Info */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Informacoes de Contato</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">Endereco</label>
            <input
              {...register('contact_address')}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="Rua, numero, cidade, estado"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Telefone</label>
            <input
              {...register('contact_phone')}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="(11) 99999-9999"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              {...register('contact_email')}
              type="email"
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="contato@empresa.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Website</label>
            <input
              {...register('contact_website')}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="https://www.empresa.com"
            />
          </div>
        </div>
      </section>

      {/* Submit */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={updateBranding.isPending}
          className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {updateBranding.isPending ? 'Salvando...' : 'Salvar Alteracoes'}
        </button>
      </div>

      {updateBranding.isSuccess && (
        <p className="text-sm text-green-600">Alteracoes salvas com sucesso!</p>
      )}
    </form>
  )
}
