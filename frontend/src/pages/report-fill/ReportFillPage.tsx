import {
  ArrowLeft,
  Loader2,
  Save,
  CheckCircle,
  FileDown,
  ListChecks,
  RefreshCw,
} from 'lucide-react'
import type { SignatureField } from '@/features/signature'
import { RevisionButton } from '@/features/report/components/RevisionButton'
import { RevisionHistory } from '@/features/report/components/RevisionHistory'
import { useReportFillState } from './useReportFillState'
import { AutoSaveStatus } from './AutoSaveStatus'
import { InfoFieldsStep } from './InfoFieldsStep'
import { ChecklistStep } from './ChecklistStep'
import { PhotoSection } from './PhotoSection'
import { SignatureStep } from './SignatureStep'
import { CertificateSelector } from './CertificateSelector'

export function ReportFillPage() {
  const state = useReportFillState()

  const {
    report,
    isLoading,
    error,
    navigate,
    reportId,
    isReadOnly,
    progress,
    autoSave,
    // Form state
    infoValues,
    setInfoValues,
    responses,
    setResponses,
    expandedSections,
    showComments,
    showDraftRecovery,
    // Photo
    photos,
    cameraOpen,
    setCameraOpen,
    // Download
    isDownloading,
    // Signatures
    signatures,
    // Certificate
    showCertificateModal,
    setShowCertificateModal,
    // Actions
    toggleSection,
    toggleComment,
    handleSave,
    handlePreFillAll,
    handleOpenCompleteModal,
    handleComplete,
    handleDownloadPdf,
    recoverDraft,
    dismissDraftRecovery,
    openCamera,
    handlePhotoCapture,
    handlePhotoDelete,
    getResponseId,
    handleAddSignature,
    handleDeleteSignature,
    completeMutation,
    // Branding
    tenantLogo,
    watermarkText,
  } = state

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erro ao carregar relatorio</p>
        <button
          onClick={() => navigate('/reports')}
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/reports')}
            className="flex items-center gap-1 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5" />
            Voltar
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{report.title}</h1>
              {report.revision_number > 0 && (
                <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium">
                  Rev. {report.revision_number}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500">
              Template: {report.template_snapshot.name} | Status: {report.status}
            </p>
          </div>
        </div>

        {!isReadOnly && (
          <div className="flex items-center gap-3">
            <AutoSaveStatus
              status={autoSave.status}
              lastSaved={autoSave.lastSaved}
              error={autoSave.error}
            />
            <button
              onClick={handlePreFillAll}
              className="flex items-center gap-2 px-4 py-2 text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 border border-blue-200"
              title="Preencher todos os campos com a primeira opcao"
            >
              <ListChecks className="h-4 w-4" />
              Preencher Tudo
            </button>
            <button
              onClick={handleSave}
              disabled={autoSave.isSaving}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {autoSave.isSaving ? 'Salvando...' : 'Salvar'}
            </button>
            <button
              onClick={handleOpenCompleteModal}
              disabled={completeMutation.isPending || autoSave.isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" />
              Concluir
            </button>
          </div>
        )}

        {isReadOnly && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">
              {report.status === 'completed' ? 'Relatorio concluido' : 'Relatorio arquivado'}
            </span>
            <RevisionButton reportId={reportId!} reportStatus={report.status} />
            <button
              onClick={handleDownloadPdf}
              disabled={isDownloading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isDownloading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileDown className="h-4 w-4" />
              )}
              {isDownloading ? 'Baixando...' : 'Baixar PDF'}
            </button>
          </div>
        )}
      </div>

      {/* Draft Recovery Banner */}
      {showDraftRecovery && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <RefreshCw className="h-5 w-5 text-yellow-600" />
            <p className="text-sm text-yellow-800">
              Foi encontrado um rascunho nao salvo. Deseja recuperar?
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={dismissDraftRecovery}
              className="px-3 py-1 text-sm text-yellow-700 hover:bg-yellow-100 rounded"
            >
              Descartar
            </button>
            <button
              onClick={recoverDraft}
              className="px-3 py-1 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
            >
              Recuperar
            </button>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Progresso</span>
          <span className="text-sm text-gray-500">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Revision History */}
      <RevisionHistory
        reportId={reportId!}
        currentReportId={reportId!}
        revisionNumber={report.revision_number}
      />

      {/* Info Fields */}
      <InfoFieldsStep
        infoFields={report.template_snapshot.info_fields}
        infoValues={infoValues}
        onInfoValueChange={(label, value) =>
          setInfoValues((prev) => ({ ...prev, [label]: value }))
        }
        isReadOnly={isReadOnly}
      />

      {/* Checklist */}
      <ChecklistStep
        sections={report.template_snapshot.sections}
        responses={responses}
        onResponseChange={(fieldKey, value) => {
          setResponses((prev) => ({
            ...prev,
            [fieldKey]: { ...prev[fieldKey], value, comment: prev[fieldKey]?.comment || '' },
          }))
        }}
        onCommentChange={(fieldKey, comment) => {
          setResponses((prev) => ({
            ...prev,
            [fieldKey]: { ...prev[fieldKey], value: prev[fieldKey]?.value || '', comment },
          }))
        }}
        expandedSections={expandedSections}
        onToggleSection={toggleSection}
        showComments={showComments}
        onToggleComment={toggleComment}
        isReadOnly={isReadOnly}
        photos={photos}
        getResponseId={getResponseId}
        onOpenCamera={openCamera}
        onDeletePhoto={handlePhotoDelete}
      />

      {/* Signatures */}
      <SignatureStep
        signatures={signatures}
        signatureFields={report.template_snapshot.signature_fields as SignatureField[]}
        onAddSignature={handleAddSignature}
        onDeleteSignature={handleDeleteSignature}
        isReadOnly={isReadOnly}
      />

      {/* Camera Capture Modal */}
      <PhotoSection
        cameraOpen={cameraOpen}
        onCameraClose={() => setCameraOpen(false)}
        onCapture={handlePhotoCapture}
        tenantLogo={tenantLogo}
        projectName={report?.title}
        watermarkText={watermarkText}
      />

      {/* Certificate Selection Modal */}
      <CertificateSelector
        isOpen={showCertificateModal}
        onClose={() => setShowCertificateModal(false)}
        onConfirm={handleComplete}
        reportId={reportId!}
        isLoading={completeMutation.isPending}
      />
    </div>
  )
}
