import { useState } from 'react'
import {
  Search,
  Loader2,
  Award,
  Pencil,
  Trash2,
  Upload,
  Hash,
  FileText,
} from 'lucide-react'
import { type Certificate } from '../api/certificateApi'
import { useCertificates, useDeleteCertificate } from '../hooks/useCertificates'

interface CertificateListProps {
  onEdit: (certificate: Certificate) => void
  onUpload: (certificate: Certificate) => void
}

export function CertificateList({ onEdit, onUpload }: CertificateListProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, error } = useCertificates({
    search: searchTerm || undefined,
    limit: 100,
  })

  const deleteMutation = useDeleteCertificate()

  const handleDelete = async (id: string, name: string) => {
    if (!window.confirm(`Deseja realmente excluir o certificado "${name}"?`)) {
      return
    }
    await deleteMutation.mutateAsync(id)
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
      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Buscar por equipamento ou numero de serie..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
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
              <div className="flex items-center justify-between gap-4">
                {/* Certificate Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <Award className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <span className="font-semibold text-gray-900">
                      {cert.equipment_name}
                    </span>
                    {cert.file_key ? (
                      <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full flex items-center gap-1">
                        <FileText className="h-3 w-3" />
                        PDF
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-500 rounded-full">
                        Sem PDF
                      </span>
                    )}
                  </div>
                  {cert.serial_number && (
                    <div className="mt-1 flex items-center gap-1 text-sm text-gray-500">
                      <Hash className="h-3.5 w-3.5" />
                      S/N: {cert.serial_number}
                    </div>
                  )}
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
