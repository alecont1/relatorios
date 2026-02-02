import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { templateApi } from '@/features/template/api/templateApi'
import { AccordionSection, InfoFieldsConfigurator } from '@/features/template/components'

export function TemplateConfigPage() {
  const { templateId } = useParams<{ templateId: string }>()
  const navigate = useNavigate()

  const {
    data: template,
    isLoading: isLoadingTemplate,
    error: templateError,
  } = useQuery({
    queryKey: ['template', templateId],
    queryFn: () => templateApi.get(templateId!),
    enabled: !!templateId,
  })

  const {
    data: infoFieldsData,
    isLoading: isLoadingInfoFields,
    refetch: refetchInfoFields,
  } = useQuery({
    queryKey: ['infoFields', templateId],
    queryFn: () => templateApi.getInfoFields(templateId!),
    enabled: !!templateId,
  })

  const {
    data: signatureFieldsData,
    isLoading: isLoadingSignatureFields,
  } = useQuery({
    queryKey: ['signatureFields', templateId],
    queryFn: () => templateApi.getSignatureFields(templateId!),
    enabled: !!templateId,
  })

  const isLoading = isLoadingTemplate || isLoadingInfoFields || isLoadingSignatureFields

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (templateError || !template) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erro ao carregar template</p>
        <button
          onClick={() => navigate('/templates')}
          className="mt-4 text-blue-600 hover:underline"
        >
          Voltar para lista
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/templates')}
          className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          Voltar
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{template.name}</h1>
          <p className="text-sm text-gray-500">
            Codigo: {template.code} | Versao: v{template.version}
          </p>
        </div>
      </div>

      {/* Configuration Sections */}
      <div className="space-y-4">
        {/* Info Fields */}
        <AccordionSection
          title="Campos de Informacao"
          badge={infoFieldsData?.total || 0}
          defaultOpen={true}
        >
          <p className="text-sm text-gray-500 mb-4">
            Configure os campos de metadados do projeto que aparecem no topo do relatorio
            (ex: Nome do Projeto, Data, Localizacao).
          </p>
          <InfoFieldsConfigurator
            templateId={templateId!}
            initialFields={infoFieldsData?.info_fields || []}
            onUpdate={() => refetchInfoFields()}
          />
        </AccordionSection>

        {/* Checklist Sections */}
        <AccordionSection
          title="Secoes do Checklist"
          badge={template.sections?.length || 0}
        >
          <p className="text-sm text-gray-500 mb-4">
            Visualize as secoes e campos do checklist importados do Excel.
            Use o Plano 05-05 para configurar fotos e comentarios por campo.
          </p>
          {template.sections && template.sections.length > 0 ? (
            <div className="space-y-3">
              {template.sections.map((section, idx) => (
                <div key={section.id || idx} className="rounded border border-gray-200 p-3">
                  <h4 className="font-medium text-gray-900 mb-2">
                    {idx + 1}. {section.name}
                  </h4>
                  <ul className="space-y-1 pl-4">
                    {section.fields.map((field, fidx) => (
                      <li
                        key={field.id || fidx}
                        className="text-sm text-gray-600 flex items-center gap-2"
                      >
                        <span className="w-5 text-gray-400">{fidx + 1}.</span>
                        <span>{field.label}</span>
                        <span className="text-xs text-gray-400">({field.field_type})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center py-4 text-gray-500">
              Nenhuma secao configurada
            </p>
          )}
        </AccordionSection>

        {/* Signature Fields */}
        <AccordionSection
          title="Campos de Assinatura"
          badge={signatureFieldsData?.total || 0}
        >
          <p className="text-sm text-gray-500 mb-4">
            Configure quem deve assinar o relatorio (ex: Tecnico Executor, Responsavel Tecnico).
            A implementacao completa sera feita no Plano 05-05.
          </p>
          {signatureFieldsData && signatureFieldsData.signature_fields.length > 0 ? (
            <div className="space-y-2">
              {signatureFieldsData.signature_fields.map((field) => (
                <div
                  key={field.id}
                  className="flex items-center justify-between rounded border border-gray-200 px-3 py-2"
                >
                  <span className="font-medium text-gray-900">{field.role_name}</span>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      field.required
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {field.required ? 'Obrigatorio' : 'Opcional'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center py-4 text-gray-500">
              Nenhum campo de assinatura configurado
            </p>
          )}
        </AccordionSection>
      </div>
    </div>
  )
}
