import { useState, useRef } from 'react'
import { X, Upload, FileText, Loader2, CheckCircle } from 'lucide-react'
import { type Certificate } from '../api/certificateApi'
import { useUploadCertificateFile } from '../hooks/useCertificates'

interface CertificateUploadProps {
  isOpen: boolean
  onClose: () => void
  certificate: Certificate | null
}

export function CertificateUpload({ isOpen, onClose, certificate }: CertificateUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const uploadMutation = useUploadCertificateFile()

  if (!isOpen || !certificate) return null

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('Apenas arquivos PDF sao aceitos.')
        return
      }
      setSelectedFile(file)
      setUploadSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile || !certificate) return

    try {
      await uploadMutation.mutateAsync({
        id: certificate.id,
        file: selectedFile,
      })
      setUploadSuccess(true)
      setSelectedFile(null)
      // Auto-close after success
      setTimeout(() => {
        handleClose()
      }, 1500)
    } catch {
      // Error handled by mutation
    }
  }

  const handleClose = () => {
    setSelectedFile(null)
    setUploadSuccess(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    onClose()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
          {/* Header */}
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Upload de PDF
            </h2>
            <button
              onClick={handleClose}
              className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Certificate info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-900">
              {certificate.equipment_name}
            </p>
            <p className="text-xs text-gray-500">
              {certificate.certificate_number}
            </p>
          </div>

          {/* Upload Area */}
          <div className="space-y-4">
            {uploadSuccess ? (
              <div className="flex flex-col items-center py-8 text-green-600">
                <CheckCircle className="h-12 w-12 mb-3" />
                <p className="font-medium">Upload realizado com sucesso!</p>
              </div>
            ) : (
              <>
                {/* File Input Area */}
                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
                >
                  <Upload className="h-10 w-10 text-gray-400 mx-auto mb-3" />
                  <p className="text-sm text-gray-600">
                    Clique para selecionar um arquivo PDF
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Apenas arquivos PDF
                  </p>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {/* Selected File */}
                {selectedFile && (
                  <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {selectedFile.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedFile(null)
                        if (fileInputRef.current) fileInputRef.current.value = ''
                      }}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}

                {/* Error */}
                {uploadMutation.isError && (
                  <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    Erro ao enviar arquivo. Tente novamente.
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={!selectedFile || uploadMutation.isPending}
                    className="flex flex-1 items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {uploadMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Enviando...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Enviar PDF
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
