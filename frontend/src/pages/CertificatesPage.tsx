import { useState } from 'react'
import { Plus, Award } from 'lucide-react'
import {
  CertificateList,
  CertificateForm,
  CertificateUpload,
  type Certificate,
} from '@/features/certificate'

export function CertificatesPage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [editingCertificate, setEditingCertificate] = useState<Certificate | null>(null)
  const [uploadCertificate, setUploadCertificate] = useState<Certificate | null>(null)

  const handleEdit = (certificate: Certificate) => {
    setEditingCertificate(certificate)
    setIsFormOpen(true)
  }

  const handleUpload = (certificate: Certificate) => {
    setUploadCertificate(certificate)
    setIsUploadOpen(true)
  }

  const handleCloseForm = () => {
    setIsFormOpen(false)
    setEditingCertificate(null)
  }

  const handleCloseUpload = () => {
    setIsUploadOpen(false)
    setUploadCertificate(null)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Award className="h-7 w-7 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Certificados de Calibracao
            </h1>
            <p className="text-sm text-gray-500">
              Gerencie os certificados de calibracao dos equipamentos
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            setEditingCertificate(null)
            setIsFormOpen(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Novo Certificado
        </button>
      </div>

      {/* Certificate List */}
      <CertificateList onEdit={handleEdit} onUpload={handleUpload} />

      {/* Create/Edit Modal */}
      <CertificateForm
        isOpen={isFormOpen}
        onClose={handleCloseForm}
        certificate={editingCertificate}
      />

      {/* Upload Modal */}
      <CertificateUpload
        isOpen={isUploadOpen}
        onClose={handleCloseUpload}
        certificate={uploadCertificate}
      />
    </div>
  )
}
