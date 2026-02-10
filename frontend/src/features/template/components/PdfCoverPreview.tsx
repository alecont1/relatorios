import { useTenantBranding } from '@/features/tenant/api'
import { getLogoUrl } from '@/features/tenant/types'
import type { Template, InfoField, SignatureField } from '../api/templateApi'

export interface BrandingOverride {
  logoUrl?: string
  companyName?: string
  primaryColor?: string
}

interface PdfCoverPreviewProps {
  template: Template
  infoFields: InfoField[]
  signatureFields: SignatureField[]
  brandingOverride?: BrandingOverride
}

const A4_SCALE = 0.45 // scale factor for preview
const A4_WIDTH = 210 // mm
const A4_HEIGHT = 297 // mm
const PX_WIDTH = A4_WIDTH * A4_SCALE * 2.5 // ~236px
const PX_HEIGHT = A4_HEIGHT * A4_SCALE * 2.5 // ~334px

export function PdfCoverPreview({ template, infoFields, signatureFields, brandingOverride }: PdfCoverPreviewProps) {
  const { data: branding } = useTenantBranding()

  const logoUrl = brandingOverride?.logoUrl ?? getLogoUrl(branding?.logo_primary_key)
  const companyName = brandingOverride?.companyName ?? branding?.name ?? 'Empresa'
  const primaryColor = brandingOverride?.primaryColor ?? branding?.brand_color_primary ?? '#2563eb'

  return (
    <div className="space-y-6">
      <p className="text-sm text-gray-500">
        Visualizacao aproximada de como o relatorio ficara em PDF.
      </p>

      <div className="flex flex-wrap gap-6 justify-center">
        {/* Cover Page */}
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 text-center">Capa</p>
          <div
            className="bg-white border border-gray-300 rounded shadow-md overflow-hidden flex flex-col"
            style={{ width: PX_WIDTH, height: PX_HEIGHT }}
          >
            {/* Top color bar */}
            <div
              className="h-2 flex-shrink-0"
              style={{ backgroundColor: primaryColor }}
            />

            {/* Logo area */}
            <div className="flex justify-center pt-6 pb-3 px-4">
              {logoUrl ? (
                <img
                  src={logoUrl}
                  alt="Logo"
                  className="max-h-10 max-w-[120px] object-contain"
                />
              ) : (
                <div className="h-10 w-24 bg-gray-200 rounded flex items-center justify-center">
                  <span className="text-[8px] text-gray-400">LOGO</span>
                </div>
              )}
            </div>

            {/* Company name */}
            <div className="text-center px-4 pb-2">
              <p className="text-[9px] font-bold text-gray-800 uppercase tracking-wide">
                {companyName}
              </p>
            </div>

            {/* Divider */}
            <div className="mx-6 border-t border-gray-200" />

            {/* Report title */}
            <div className="text-center px-4 py-4 flex-shrink-0">
              <p
                className="text-[11px] font-bold leading-tight"
                style={{ color: primaryColor }}
              >
                {template.title || template.name}
              </p>
              <p className="text-[7px] text-gray-400 mt-1">
                {template.code} - v{template.version}
              </p>
            </div>

            {/* Info fields preview */}
            <div className="px-5 space-y-1.5 flex-1">
              {infoFields.slice(0, 5).map((field) => (
                <div key={field.id} className="flex items-baseline gap-1">
                  <span className="text-[7px] text-gray-500 flex-shrink-0">
                    {field.label}:
                  </span>
                  <span className="flex-1 border-b border-dotted border-gray-300 text-[7px] text-gray-300">
                    &nbsp;
                  </span>
                </div>
              ))}
            </div>

            {/* Signature area */}
            {signatureFields.length > 0 && (
              <div className="px-5 pb-4 pt-3">
                <div className="flex gap-3 justify-center">
                  {signatureFields.slice(0, 3).map((sig) => (
                    <div key={sig.id} className="text-center flex-1">
                      <div className="border-t border-gray-400 mt-3 pt-0.5">
                        <span className="text-[6px] text-gray-500">{sig.role_name}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Bottom bar */}
            <div
              className="h-1 flex-shrink-0 mt-auto"
              style={{ backgroundColor: primaryColor }}
            />
          </div>
        </div>

        {/* Content Page */}
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 text-center">Pagina de Conteudo</p>
          <div
            className="bg-white border border-gray-300 rounded shadow-md overflow-hidden flex flex-col"
            style={{ width: PX_WIDTH, height: PX_HEIGHT }}
          >
            {/* Header with logo */}
            <div
              className="flex items-center justify-between px-3 py-1.5 flex-shrink-0"
              style={{ backgroundColor: `${primaryColor}10` }}
            >
              <div className="flex items-center gap-2">
                {logoUrl ? (
                  <img
                    src={logoUrl}
                    alt="Logo"
                    className="max-h-4 max-w-[40px] object-contain"
                  />
                ) : (
                  <div className="h-4 w-10 bg-gray-200 rounded" />
                )}
                <span className="text-[6px] text-gray-500">{companyName}</span>
              </div>
              <span className="text-[6px] text-gray-400">
                REL-0001
              </span>
            </div>

            {/* Section title */}
            <div className="px-3 pt-3 pb-1">
              <p
                className="text-[8px] font-bold"
                style={{ color: primaryColor }}
              >
                {template.sections?.[0]?.name ?? 'Secao de Checklist'}
              </p>
            </div>

            {/* Simulated table */}
            <div className="px-3 flex-1">
              <div className="border border-gray-200 rounded overflow-hidden">
                {/* Table header */}
                <div
                  className="flex px-2 py-1"
                  style={{ backgroundColor: `${primaryColor}15` }}
                >
                  <span className="text-[6px] font-bold text-gray-700 flex-1">Item</span>
                  <span className="text-[6px] font-bold text-gray-700 w-12 text-center">Status</span>
                  <span className="text-[6px] font-bold text-gray-700 w-12 text-center">Foto</span>
                </div>
                {/* Table rows */}
                {(template.sections?.[0]?.fields ?? []).slice(0, 8).map((field, idx) => (
                  <div
                    key={idx}
                    className={`flex px-2 py-0.5 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                  >
                    <span className="text-[6px] text-gray-600 flex-1 truncate">
                      {field.label}
                    </span>
                    <span className="text-[6px] text-gray-400 w-12 text-center">
                      --
                    </span>
                    <span className="text-[6px] text-gray-400 w-12 text-center">
                      {field.photo_config ? 'Sim' : '--'}
                    </span>
                  </div>
                ))}
                {(template.sections?.[0]?.fields?.length ?? 0) === 0 && (
                  <div className="px-2 py-2">
                    <span className="text-[6px] text-gray-400">
                      Campos do checklist aparecerao aqui
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-3 py-1 border-t border-gray-200 flex-shrink-0">
              <span className="text-[5px] text-gray-400">
                {template.code} v{template.version}
              </span>
              <span className="text-[5px] text-gray-400">
                Pagina 2
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
