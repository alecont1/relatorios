import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, FileText, Check, Calendar, Building2, Wrench, Award, Loader2 } from 'lucide-react'
import { certificateApi, type Certificate } from '@/features/certificate'

interface CertificateSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (selectedCertificates: Certificate[]) => void
  reportId: string
  isLoading?: boolean
}

export function CertificateSelectionModal({
  isOpen,
  onClose,
  onConfirm,
  reportId,
  isLoading = false,
}: CertificateSelectionModalProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [isLinking, setIsLinking] = useState(false)

  // Fetch certificates from API
  const { data, isLoading: isFetching } = useQuery({
    queryKey: ['certificates', 'list', { search: searchTerm || undefined }],
    queryFn: () => certificateApi.list({ search: searchTerm || undefined, limit: 100 }),
    enabled: isOpen,
  })

  if (!isOpen) return null

  const certificates = data?.certificates || []

  const toggleCertificate = (id: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }

  const handleConfirm = async () => {
    const selected = certificates.filter((c) => selectedIds.has(c.id))

    // Link certificates to report via API if any are selected
    if (selectedIds.size > 0) {
      setIsLinking(true)
      try {
        await certificateApi.linkToReport(reportId, Array.from(selectedIds))
      } catch (error) {
        console.error('Failed to link certificates:', error)
      } finally {
        setIsLinking(false)
      }
    }

    onConfirm(selected)
  }

  const getStatusBadge = (status: Certificate['status']) => {
    switch (status) {
      case 'valid':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
            Valido
          </span>
        )
      case 'expiring':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">
            Vencendo
          </span>
        )
      case 'expired':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
            Vencido
          </span>
        )
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('pt-BR')
  }

  const isPending = isLoading || isLinking

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b bg-gradient-to-r from-blue-600 to-blue-700 rounded-t-xl">
          <div className="flex items-center gap-3">
            <Award className="h-6 w-6 text-white" />
            <div>
              <h2 className="text-lg font-semibold text-white">
                Certificados de Calibracao
              </h2>
              <p className="text-sm text-blue-100">
                Selecione os certificados para anexar ao relatorio
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b bg-gray-50">
          <input
            type="text"
            placeholder="Buscar por equipamento, numero ou fabricante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Certificate List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isFetching ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : certificates.length > 0 ? (
            certificates.map((cert) => (
              <div
                key={cert.id}
                onClick={() => toggleCertificate(cert.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedIds.has(cert.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Checkbox */}
                  <div
                    className={`flex-shrink-0 w-6 h-6 rounded-md border-2 flex items-center justify-center mt-1 ${
                      selectedIds.has(cert.id)
                        ? 'bg-blue-500 border-blue-500'
                        : 'border-gray-300'
                    }`}
                  >
                    {selectedIds.has(cert.id) && (
                      <Check className="h-4 w-4 text-white" />
                    )}
                  </div>

                  {/* Certificate Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                      <span className="font-semibold text-gray-900">
                        {cert.certificate_number}
                      </span>
                      {getStatusBadge(cert.status)}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                      <div className="flex items-center gap-2">
                        <Wrench className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-gray-500">Equipamento</p>
                          <p className="font-medium text-gray-900">{cert.equipment_name}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-gray-500">Fabricante/Modelo</p>
                          <p className="font-medium text-gray-900">
                            {cert.manufacturer || '-'} {cert.model || ''}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <div>
                          <p className="text-gray-500">Validade</p>
                          <p className="font-medium text-gray-900">
                            {formatDate(cert.expiry_date)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="mt-2 text-xs text-gray-500">
                      {cert.serial_number && <>S/N: {cert.serial_number}</>}
                      {cert.serial_number && cert.laboratory && <> | </>}
                      {cert.laboratory && <>Lab: {cert.laboratory}</>}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>Nenhum certificado encontrado</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 rounded-b-xl">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {selectedIds.size} certificado(s) selecionado(s)
            </p>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                disabled={isPending}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={isPending}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Gerando PDF...
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4" />
                    Concluir e Gerar PDF
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export type { Certificate }
