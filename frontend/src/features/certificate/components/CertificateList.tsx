import { useState } from 'react'
import {
  Search,
  Loader2,
  Award,
  Pencil,
  Trash2,
  Upload,
  Calendar,
  Building2,
  Wrench,
  Hash,
  FlaskConical,
} from 'lucide-react'
import { type Certificate } from '../api/certificateApi'
import { useCertificates, useDeleteCertificate } from '../hooks/useCertificates'

interface CertificateListProps {
  onEdit: (certificate: Certificate) => void
  onUpload: (certificate: Certificate) => void
}

export function CertificateList({ onEdit, onUpload }: CertificateListProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data, isLoading, error } = useCertificates({
    search: searchTerm || undefined,
    status: statusFilter || undefined,
    limit: 100,
  })

  const deleteMutation = useDeleteCertificate()

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Deseja realmente excluir o certificado "${name}"?`)) {
      return
    }
    await deleteMutation.mutateAsync(id)
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erro ao carregar certificados</p>
      </div>
    )
  }

  const certificates = data?.certificates || []

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por equipamento, numero ou fabricante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Todos</option>
          <option value="valid">Valido</option>
          <option value="expiring">Vencendo</option>
          <option value="expired">Vencido</option>
        </select>
      </div>

      {/* Certificate Cards */}
      {certificates.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Nenhum certificado encontrado</p>
        </div>
      ) : (
        <div className="space-y-3">
          {certificates.map((cert) => (
            <div
              key={cert.id}
              className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md hover:border-gray-300 transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Certificate Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-3">
                    <Award className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <span className="font-semibold text-gray-900">
                      {cert.certificate_number}
                    </span>
                    {getStatusBadge(cert.status)}
                    {cert.file_key && (
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                        PDF
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    <div className="flex items-center gap-2">
                      <Wrench className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <div>
                        <p className="text-gray-500">Equipamento</p>
                        <p className="font-medium text-gray-900">{cert.equipment_name}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <div>
                        <p className="text-gray-500">Fabricante/Modelo</p>
                        <p className="font-medium text-gray-900">
                          {cert.manufacturer || '-'} {cert.model || ''}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <div>
                        <p className="text-gray-500">Validade</p>
                        <p className="font-medium text-gray-900">
                          {formatDate(cert.calibration_date)} - {formatDate(cert.expiry_date)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                    {cert.serial_number && (
                      <span className="flex items-center gap-1">
                        <Hash className="h-3 w-3" />
                        S/N: {cert.serial_number}
                      </span>
                    )}
                    {cert.laboratory && (
                      <span className="flex items-center gap-1">
                        <FlaskConical className="h-3 w-3" />
                        Lab: {cert.laboratory}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => onEdit(cert)}
                    className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Editar"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onUpload(cert)}
                    className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Upload PDF"
                  >
                    <Upload className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(cert.id, cert.equipment_name)}
                    disabled={deleteMutation.isPending}
                    className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    title="Excluir"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Total count */}
      {data && data.total > 0 && (
        <p className="text-sm text-gray-500">
          {data.total} certificado(s) encontrado(s)
        </p>
      )}
    </div>
  )
}
