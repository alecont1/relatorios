import { useState } from 'react'
import { Loader2, FileText, AlertCircle, Download, CheckCircle2, Eye, Sparkles } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { reportApi, type CreateReportData } from '@/features/report/api/reportApi'
import { useOnboardingStatus, useReportPdfBlob } from '../api'

interface FirstReportStepProps {
  onComplete: () => void
}

export function FirstReportStep({ onComplete }: FirstReportStepProps) {
  const queryClient = useQueryClient()
  const { data: status } = useOnboardingStatus()
  const [title, setTitle] = useState('Inspecao Quadro Principal - Teste')
  const [error, setError] = useState('')
  const [createdReportId, setCreatedReportId] = useState<string | null>(null)

  const demoTemplateId = status?.metadata_json?.demo_template_id as string | undefined
  const existingReportId = status?.metadata_json?.demo_report_id as string | undefined

  // Use either the just-created report or one from a previous session
  const reportId = createdReportId ?? existingReportId ?? null
  const { blobUrl, isLoading: pdfLoading, error: pdfError, downloadPdf } = useReportPdfBlob(reportId)

  const createReport = useMutation({
    mutationFn: (data: CreateReportData) => reportApi.create(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setCreatedReportId(result.id)
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      setError(axiosError.response?.data?.detail || 'Erro ao criar relatorio')
    },
  })

  const handleCreate = () => {
    if (!demoTemplateId || !title.trim()) return

    setError('')
    createReport.mutate({
      template_id: demoTemplateId,
      project_id: '00000000-0000-0000-0000-000000000000',
      title: title.trim(),
    })
  }

  const hasReport = !!reportId

  if (!demoTemplateId) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Teste Real</h2>
          <p className="mt-1 text-sm text-gray-500">
            Crie um relatorio e veja o PDF gerado com a sua marca
          </p>
        </div>
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-600" />
            <div>
              <p className="font-medium text-yellow-900">Template nao encontrado</p>
              <p className="mt-1 text-sm text-yellow-700">
                Volte ao passo 2 para clonar o template demo ou pule este passo.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Teste Real</h2>
        <p className="mt-1 text-sm text-gray-500">
          Crie um relatorio e veja o PDF gerado com a sua marca
        </p>
      </div>

      {/* Create report form - only show if no report yet */}
      {!hasReport && (
        <div className="onboarding-report-form space-y-4 rounded-lg border p-6">
          <div className="flex items-start gap-3 rounded-lg bg-blue-50 p-3">
            <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-blue-900">Template: CPQ11 - Demo</p>
              <p className="text-blue-700">O relatorio sera criado como rascunho com dados de exemplo</p>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Titulo do Relatorio *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Inspecao Quadro Principal - Fevereiro 2026"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
          )}

          <button
            onClick={handleCreate}
            disabled={createReport.isPending || !title.trim()}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {createReport.isPending ? (
              <span className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Criando relatorio...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Criar e Gerar PDF
              </span>
            )}
          </button>
        </div>
      )}

      {/* PDF Preview Section - shows after report is created */}
      {hasReport && (
        <div className="space-y-4">
          {/* Status bar */}
          <div className="rounded-lg border border-green-200 bg-green-50 p-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
              <div className="flex-1">
                <p className="font-medium text-green-900">
                  Relatorio criado com sucesso!
                </p>
                <p className="text-sm text-green-700">
                  Veja abaixo como seu PDF fica com a marca configurada
                </p>
              </div>
            </div>
          </div>

          {/* PDF iframe or loading */}
          <div className="rounded-lg border bg-white overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b bg-gray-50">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-700">Preview do PDF</span>
              </div>
              {blobUrl && (
                <button
                  onClick={downloadPdf}
                  className="flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 transition-colors"
                >
                  <Download className="h-3.5 w-3.5" />
                  Baixar PDF
                </button>
              )}
            </div>

            <div className="bg-gray-100">
              {pdfLoading && (
                <div className="flex flex-col items-center justify-center py-20">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-3" />
                  <p className="text-sm text-gray-500">Gerando seu PDF...</p>
                  <p className="text-xs text-gray-400 mt-1">Isso pode levar alguns segundos</p>
                </div>
              )}

              {pdfError && (
                <div className="flex flex-col items-center justify-center py-20">
                  <AlertCircle className="h-8 w-8 text-amber-500 mb-3" />
                  <p className="text-sm text-gray-600">{pdfError}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    O relatorio foi criado. Voce pode gerar o PDF depois na tela de relatorios.
                  </p>
                </div>
              )}

              {blobUrl && (
                <iframe
                  src={blobUrl}
                  className="w-full border-0"
                  style={{ height: '600px' }}
                  title="Preview do PDF do relatorio"
                />
              )}
            </div>
          </div>

          {/* Complete onboarding button */}
          <div className="flex items-center justify-between pt-2">
            <p className="text-sm text-gray-500">
              Pronto! Agora voce sabe como fica seu relatorio.
            </p>
            <button
              onClick={onComplete}
              className="flex items-center gap-2 rounded-lg bg-green-600 px-6 py-2.5 text-white font-medium hover:bg-green-700 transition-colors"
            >
              <CheckCircle2 className="h-4 w-4" />
              Concluir Onboarding
            </button>
          </div>
        </div>
      )}

      {/* If report exists from previous session, show button to complete */}
      {existingReportId && !createdReportId && !blobUrl && !pdfLoading && (
        <div className="flex justify-start">
          <button
            onClick={onComplete}
            className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
          >
            Concluir Passo
          </button>
        </div>
      )}
    </div>
  )
}
