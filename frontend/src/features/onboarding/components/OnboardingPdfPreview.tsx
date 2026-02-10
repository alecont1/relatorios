import { useTenantBranding } from '@/features/tenant/api'
import { getLogoUrl } from '@/features/tenant/types'
import { Camera, CheckCircle, XCircle, MinusCircle, PenTool } from 'lucide-react'

interface Section {
  name: string
  fields: Array<{
    label: string
    field_type: string
    photo_config?: { required: boolean; min_count: number; max_count: number } | null
  }>
}

interface OnboardingPdfPreviewProps {
  templateName: string
  templateCode: string
  sections: Section[]
}

const A4_SCALE = 0.5
const A4_WIDTH = 210
const A4_HEIGHT = 297
const PX_WIDTH = A4_WIDTH * A4_SCALE * 2.5
const PX_HEIGHT = A4_HEIGHT * A4_SCALE * 2.5

// Mock responses for preview
const MOCK_RESPONSES = ['Conforme', 'Conforme', 'Nao Conforme', 'Conforme', 'N/A', 'Conforme', 'Conforme', 'Conforme']

function getResponseColor(response: string): string {
  if (response === 'Conforme') return '#16a34a'
  if (response === 'Nao Conforme') return '#dc2626'
  return '#9ca3af'
}

function getResponseIcon(response: string) {
  if (response === 'Conforme') return <CheckCircle className="h-2.5 w-2.5" style={{ color: '#16a34a' }} />
  if (response === 'Nao Conforme') return <XCircle className="h-2.5 w-2.5" style={{ color: '#dc2626' }} />
  return <MinusCircle className="h-2.5 w-2.5" style={{ color: '#9ca3af' }} />
}

export function OnboardingPdfPreview({ templateName, templateCode, sections }: OnboardingPdfPreviewProps) {
  const { data: branding } = useTenantBranding()

  const logoUrl = getLogoUrl(branding?.logo_primary_key)
  const companyName = branding?.name ?? 'Empresa'
  const primaryColor = branding?.brand_color_primary ?? '#2563eb'

  const firstSection = sections[0]

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
          Exemplo
        </span>
        <span className="text-xs text-gray-500">
          Preview com dados ficticios
        </span>
      </div>

      <div className="flex flex-wrap gap-4 justify-center">
        {/* Checklist Page */}
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 text-center">Checklist</p>
          <div
            className="bg-white border border-gray-300 rounded shadow-md overflow-hidden flex flex-col"
            style={{ width: PX_WIDTH, height: PX_HEIGHT }}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-3 py-1.5 flex-shrink-0"
              style={{ backgroundColor: `${primaryColor}10` }}
            >
              <div className="flex items-center gap-2">
                {logoUrl ? (
                  <img src={logoUrl} alt="Logo" className="max-h-4 max-w-[40px] object-contain" />
                ) : (
                  <div className="h-4 w-10 bg-gray-200 rounded" />
                )}
                <span className="text-[6px] text-gray-500">{companyName}</span>
              </div>
              <span className="text-[6px] text-gray-400">{templateCode}</span>
            </div>

            {/* Section title */}
            {firstSection && (
              <div className="px-3 pt-2 pb-1">
                <p className="text-[8px] font-bold" style={{ color: primaryColor }}>
                  {firstSection.name}
                </p>
              </div>
            )}

            {/* Checklist table with mock data */}
            <div className="px-3 flex-1">
              <div className="border border-gray-200 rounded overflow-hidden">
                {/* Table header */}
                <div
                  className="flex px-2 py-1"
                  style={{ backgroundColor: `${primaryColor}15` }}
                >
                  <span className="text-[6px] font-bold text-gray-700 flex-1">Item</span>
                  <span className="text-[6px] font-bold text-gray-700 w-14 text-center">Status</span>
                  <span className="text-[6px] font-bold text-gray-700 w-8 text-center">Foto</span>
                </div>

                {/* Table rows with mock responses */}
                {(firstSection?.fields ?? []).slice(0, 8).map((field, idx) => {
                  const mockResponse = MOCK_RESPONSES[idx % MOCK_RESPONSES.length]
                  return (
                    <div
                      key={idx}
                      className={`flex items-center px-2 py-0.5 ${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}
                    >
                      <span className="text-[6px] text-gray-600 flex-1 truncate pr-1">
                        {field.label}
                      </span>
                      <span className="w-14 flex items-center justify-center gap-0.5">
                        {getResponseIcon(mockResponse)}
                        <span className="text-[5px]" style={{ color: getResponseColor(mockResponse) }}>
                          {mockResponse === 'Nao Conforme' ? 'N/C' : mockResponse === 'Conforme' ? 'OK' : 'N/A'}
                        </span>
                      </span>
                      <span className="w-8 flex justify-center">
                        {field.photo_config ? (
                          <Camera className="h-2 w-2 text-blue-400" />
                        ) : (
                          <span className="text-[6px] text-gray-300">--</span>
                        )}
                      </span>
                    </div>
                  )
                })}
              </div>

              {/* Non-conformity comment example */}
              <div className="mt-1.5 rounded border border-red-200 bg-red-50 px-2 py-1">
                <p className="text-[5px] font-bold text-red-700">Observacao (Nao Conforme):</p>
                <p className="text-[5px] text-red-600 italic">
                  "Parafuso de fixacao solto no barramento principal"
                </p>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-3 py-1 border-t border-gray-200 flex-shrink-0">
              <span className="text-[5px] text-gray-400">{companyName}</span>
              <span className="text-[5px] text-gray-400">Pagina 2</span>
            </div>
          </div>
        </div>

        {/* Photos + Signatures Page */}
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2 text-center">Fotos & Assinaturas</p>
          <div
            className="bg-white border border-gray-300 rounded shadow-md overflow-hidden flex flex-col"
            style={{ width: PX_WIDTH, height: PX_HEIGHT }}
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-3 py-1.5 flex-shrink-0"
              style={{ backgroundColor: `${primaryColor}10` }}
            >
              <div className="flex items-center gap-2">
                {logoUrl ? (
                  <img src={logoUrl} alt="Logo" className="max-h-4 max-w-[40px] object-contain" />
                ) : (
                  <div className="h-4 w-10 bg-gray-200 rounded" />
                )}
                <span className="text-[6px] text-gray-500">{companyName}</span>
              </div>
              <span className="text-[6px] text-gray-400">{templateCode}</span>
            </div>

            {/* Photos section */}
            <div className="px-3 pt-2 pb-1">
              <p className="text-[8px] font-bold" style={{ color: primaryColor }}>
                Registro Fotografico
              </p>
            </div>

            <div className="px-3 grid grid-cols-2 gap-1.5">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="border border-gray-200 rounded overflow-hidden">
                  <div className="bg-gray-100 h-14 flex items-center justify-center">
                    <Camera className="h-4 w-4 text-gray-300" />
                  </div>
                  <div className="px-1 py-0.5 bg-gray-50">
                    <p className="text-[5px] text-gray-500 truncate">Foto {i} - Verificacao visual</p>
                    <p className="text-[4px] text-gray-400">10/02/2026 14:3{i}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Signatures section */}
            <div className="px-3 pt-3 pb-1">
              <p className="text-[8px] font-bold" style={{ color: primaryColor }}>
                Assinaturas
              </p>
            </div>

            <div className="px-3 flex gap-3 flex-1">
              {['Tecnico Responsavel', 'Supervisor'].map((role) => (
                <div key={role} className="flex-1 border border-gray-200 rounded p-1.5 flex flex-col items-center justify-end">
                  <PenTool className="h-4 w-4 text-gray-200 mb-1" />
                  <div className="w-full border-t border-gray-300 pt-0.5 text-center">
                    <p className="text-[6px] text-gray-500">{role}</p>
                    <p className="text-[5px] text-gray-400 italic">Assinatura digital</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-3 py-1 border-t border-gray-200 flex-shrink-0 mt-auto">
              <span className="text-[5px] text-gray-400">{companyName}</span>
              <span className="text-[5px] text-gray-400">Pagina 3</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
