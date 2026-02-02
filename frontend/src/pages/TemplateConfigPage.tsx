import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { templateApi, type TemplateField } from '@/features/template/api/templateApi'
import {
  AccordionSection,
  InfoFieldsConfigurator,
  SignatureFieldsConfigurator,
  ChecklistSectionsView,
  FieldConfigModal,
} from '@/features/template/components'

export function TemplateConfigPage() {
  const { templateId } = useParams<{ templateId: string }>()
  const navigate = useNavigate()

  const [selectedField, setSelectedField] = useState<TemplateField | null>(null)
  const [isFieldModalOpen, setIsFieldModalOpen] = useState(false)

  const {
    data: template,
    isLoading: isLoadingTemplate,
    error: templateError,
    refetch: refetchTemplate,
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
    refetch: refetchSignatureFields,
  } = useQuery({
    queryKey: ['signatureFields', templateId],
    queryFn: () => templateApi.getSignatureFields(templateId!),
    enabled: !!templateId,
  })

  const isLoading = isLoadingTemplate || isLoadingInfoFields || isLoadingSignatureFields

  const handleFieldClick = (field: TemplateField) => {
    setSelectedField(field)
    setIsFieldModalOpen(true)
  }

  const handleFieldModalClose = () => {
    setIsFieldModalOpen(false)
    setSelectedField(null)
  }

  const handleFieldSave = () => {
    refetchTemplate()
  }

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

  // Count total fields across all sections
  const totalFields = template.sections?.reduce(
    (acc, section) => acc + section.fields.length,
    0
  ) || 0

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
          badge={`${template.sections?.length || 0} secoes, ${totalFields} campos`}
        >
          <p className="text-sm text-gray-500 mb-4">
            Clique em um campo para configurar requisitos de fotos e comentarios.
          </p>
          <ChecklistSectionsView
            sections={template.sections || []}
            onFieldClick={handleFieldClick}
          />
        </AccordionSection>

        {/* Signature Fields */}
        <AccordionSection
          title="Campos de Assinatura"
          badge={signatureFieldsData?.total || 0}
        >
          <p className="text-sm text-gray-500 mb-4">
            Configure quem deve assinar o relatorio (ex: Tecnico Executor, Responsavel Tecnico).
          </p>
          <SignatureFieldsConfigurator
            templateId={templateId!}
            initialFields={signatureFieldsData?.signature_fields || []}
            onUpdate={() => refetchSignatureFields()}
          />
        </AccordionSection>
      </div>

      {/* Field Configuration Modal */}
      {selectedField && (
        <FieldConfigModal
          field={selectedField}
          isOpen={isFieldModalOpen}
          onClose={handleFieldModalClose}
          onSave={handleFieldSave}
        />
      )}
    </div>
  )
}
