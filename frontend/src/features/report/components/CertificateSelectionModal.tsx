import { useState } from 'react'
import { X, FileText, Check, Calendar, Building2, Wrench, Award } from 'lucide-react'

interface Certificate {
  id: string
  number: string
  equipment: string
  manufacturer: string
  model: string
  serialNumber: string
  calibrationDate: string
  expiryDate: string
  laboratory: string
  status: 'valid' | 'expiring' | 'expired'
}

// Mock data for demonstration
const MOCK_CERTIFICATES: Certificate[] = [
  {
    id: '1',
    number: 'CAL-2024-001',
    equipment: 'Multímetro Digital',
    manufacturer: 'Fluke',
    model: '87V',
    serialNumber: 'SN-12345678',
    calibrationDate: '2024-01-15',
    expiryDate: '2025-01-15',
    laboratory: 'Laboratório ABC Calibrações',
    status: 'valid',
  },
  {
    id: '2',
    number: 'CAL-2024-002',
    equipment: 'Megômetro',
    manufacturer: 'Megabras',
    model: 'MI-2552',
    serialNumber: 'SN-87654321',
    calibrationDate: '2024-02-20',
    expiryDate: '2025-02-20',
    laboratory: 'Instituto de Metrologia',
    status: 'valid',
  },
  {
    id: '3',
    number: 'CAL-2024-003',
    equipment: 'Terrômetro',
    manufacturer: 'Minipa',
    model: 'MTR-1522',
    serialNumber: 'SN-11223344',
    calibrationDate: '2024-03-10',
    expiryDate: '2025-03-10',
    laboratory: 'Calibra Brasil',
    status: 'valid',
  },
  {
    id: '4',
    number: 'CAL-2023-045',
    equipment: 'Analisador de Energia',
    manufacturer: 'Hioki',
    model: 'PW3198',
    serialNumber: 'SN-99887766',
    calibrationDate: '2023-06-15',
    expiryDate: '2024-06-15',
    laboratory: 'MetroCal Serviços',
    status: 'expiring',
  },
  {
    id: '5',
    number: 'CAL-2024-010',
    equipment: 'Termômetro Infravermelho',
    manufacturer: 'Fluke',
    model: '62 MAX+',
    serialNumber: 'SN-55667788',
    calibrationDate: '2024-04-01',
    expiryDate: '2025-04-01',
    laboratory: 'Laboratório ABC Calibrações',
    status: 'valid',
  },
  {
    id: '6',
    number: 'CAL-2024-015',
    equipment: 'Alicate Amperímetro',
    manufacturer: 'Fluke',
    model: '376 FC',
    serialNumber: 'SN-33445566',
    calibrationDate: '2024-05-20',
    expiryDate: '2025-05-20',
    laboratory: 'Instituto de Metrologia',
    status: 'valid',
  },
]

interface CertificateSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (selectedCertificates: Certificate[]) => void
  isLoading?: boolean
}

export function CertificateSelectionModal({
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
}: CertificateSelectionModalProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')

  if (!isOpen) return null

  const filteredCertificates = MOCK_CERTIFICATES.filter(
    (cert) =>
      cert.equipment.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cert.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cert.manufacturer.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const toggleCertificate = (id: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }

  const handleConfirm = () => {
    const selected = MOCK_CERTIFICATES.filter((c) => selectedIds.has(c.id))
    onConfirm(selected)
  }

  const getStatusBadge = (status: Certificate['status']) => {
    switch (status) {
      case 'valid':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">
            Válido
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
    return new Date(dateStr).toLocaleDateString('pt-BR')
  }

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
                Certificados de Calibração
              </h2>
              <p className="text-sm text-blue-100">
                Selecione os certificados para anexar ao relatório
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
            placeholder="Buscar por equipamento, número ou fabricante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Certificate List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filteredCertificates.map((cert) => (
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
                      {cert.number}
                    </span>
                    {getStatusBadge(cert.status)}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Wrench className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Equipamento</p>
                        <p className="font-medium text-gray-900">{cert.equipment}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Fabricante/Modelo</p>
                        <p className="font-medium text-gray-900">
                          {cert.manufacturer} {cert.model}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-gray-500">Validade</p>
                        <p className="font-medium text-gray-900">
                          {formatDate(cert.expiryDate)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-2 text-xs text-gray-500">
                    S/N: {cert.serialNumber} | Lab: {cert.laboratory}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {filteredCertificates.length === 0 && (
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
                disabled={isLoading}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={isLoading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin">⏳</span>
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
