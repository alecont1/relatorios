import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2, Eye } from 'lucide-react'
import { templateApi, type TemplateField } from '@/features/template/api/templateApi'
import {
  AccordionSection,
  InfoFieldsConfigurator,
  SignatureFieldsConfigurator,
  ChecklistSectionsView,
  FieldConfigModal,
  PdfCoverPreview,
} from '@/features/template/components'
import { OnboardingPdfPreview } from '@/features/onboarding/components/OnboardingPdfPreview'

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

  // Map sections for OnboardingPdfPreview format
  const previewSections = (template.sections ?? []).map((s) => ({
    name: s.name,
    fields: s.fields.map((f) => ({
      label: f.label,
      field_type: f.field_type,
      photo_config: f.photo_config as { required: boolean; min_count: number; max_count: number } | null,
    })),
  }))

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

      {/* Split layout: config + preview sidebar */}
      <div className="flex gap-6">
        {/* Configuration Sections - main content */}
        <div className="flex-1 space-y-4 min-w-0">
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

        {/* PDF Preview Sidebar - sticky, hidden on small screens */}
        <div className="hidden xl:block w-[560px] shrink-0">
          <div className="sticky top-24 space-y-4">
            <div className="flex items-center gap-2">
              <Eye className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">Preview do PDF</span>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
            </div>

            {/* Cover preview */}
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
              <p className="text-xs font-medium text-gray-500 mb-2 text-center">Capa</p>
              <div className="flex justify-center">
                <PdfCoverPreview
                  template={template}
                  infoFields={infoFieldsData?.info_fields || []}
                  signatureFields={signatureFieldsData?.signature_fields || []}
                />
              </div>
            </div>

            {/* Checklist + Photos preview */}
            {previewSections.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
                <OnboardingPdfPreview
                  templateName={template.name}
                  templateCode={template.code}
                  sections={previewSections}
                />
              </div>
            )}

            <p className="text-xs text-gray-400 text-center">
              O preview reflete a estrutura atual do template
            </p>
          </div>
        </div>
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
