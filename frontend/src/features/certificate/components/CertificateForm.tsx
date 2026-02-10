import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Loader2, Upload, FileText, CheckCircle } from 'lucide-react'
import { type Certificate } from '../api/certificateApi'
import { useCreateCertificate, useUpdateCertificate, useUploadCertificateFile } from '../hooks/useCertificates'

const certificateSchema = z.object({
  equipment_name: z.string().min(1, 'Nome do equipamento e obrigatorio'),
  serial_number: z.string().min(1, 'Numero de serie e obrigatorio'),
})

type CertificateFormData = z.infer<typeof certificateSchema>

interface CertificateFormProps {
  isOpen: boolean
  onClose: () => void
  certificate?: Certificate | null
}

export function CertificateForm({ isOpen, onClose, certificate }: CertificateFormProps) {
  const createMutation = useCreateCertificate()
  const updateMutation = useUpdateCertificate()
  const uploadMutation = useUploadCertificateFile()

  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)

  const isEditing = !!certificate

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    reset,
  } = useForm<CertificateFormData>({
    resolver: zodResolver(certificateSchema),
    defaultValues: {
      equipment_name: '',
      serial_number: '',
    },
  })

  // Reset form when certificate changes or modal opens
  useEffect(() => {
    if (isOpen) {
      setSelectedFile(null)
      setUploadSuccess(false)
      if (certificate) {
        reset({
          equipment_name: certificate.equipment_name,
          serial_number: certificate.serial_number || '',
        })
      } else {
        reset({
          equipment_name: '',
          serial_number: '',
        })
      }
    }
  }, [isOpen, certificate, reset])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('root', { message: 'Apenas arquivos PDF sao aceitos.' })
        return
      }
      setSelectedFile(file)
    }
  }

  const onSubmit = async (data: CertificateFormData) => {
    try {
      let cert: Certificate
      if (isEditing && certificate) {
        cert = await updateMutation.mutateAsync({ id: certificate.id, data })
      } else {
        // Send minimal data; backend auto-generates certificate_number and sets defaults
        cert = await createMutation.mutateAsync({
          ...data,
          certificate_number: `CERT-${Date.now()}`,
          calibration_date: new Date().toISOString().split('T')[0],
          expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        })
      }

      // Upload PDF if selected
      if (selectedFile) {
        await uploadMutation.mutateAsync({ id: cert.id, file: selectedFile })
        setUploadSuccess(true)
      }

      onClose()
    } catch (error: unknown) {
      const axiosError = error as {
        response?: { data?: { detail?: string } }
      }
      setError('root', {
        message: axiosError.response?.data?.detail || 'Erro ao salvar certificado',
      })
    }
  }

  if (!isOpen) return null

  const isPending = isSubmitting || createMutation.isPending || updateMutation.isPending || uploadMutation.isPending

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
          {/* Header */}
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? 'Editar Certificado' : 'Novo Certificado'}
            </h2>
            <button
              onClick={onClose}
              className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Equipment Name */}
            <div>
              <label
                htmlFor="equipment_name"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Nome do Equipamento *
              </label>
              <input
                {...register('equipment_name')}
                type="text"
                id="equipment_name"
                placeholder="Ex: Multimetro Digital"
                className={`block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${errors.equipment_name ? 'border-red-500' : ''}`}
              />
              {errors.equipment_name && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.equipment_name.message}
                </p>
              )}
            </div>

            {/* Serial Number */}
            <div>
              <label
                htmlFor="serial_number"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Numero de Serie *
              </label>
              <input
                {...register('serial_number')}
                type="text"
                id="serial_number"
                placeholder="Ex: SN-12345678"
                className={`block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${errors.serial_number ? 'border-red-500' : ''}`}
              />
              {errors.serial_number && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.serial_number.message}
                </p>
              )}
            </div>

            {/* PDF Upload inline */}
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Certificado PDF
              </label>
              {certificate?.file_key && !selectedFile && (
                <div className="mb-2 flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                  <span className="text-sm text-green-700">PDF ja enviado</span>
                </div>
              )}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 transition-colors"
              >
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">
                  Clique para selecionar o PDF do certificado
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
              {selectedFile && (
                <div className="mt-2 flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {selectedFile.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
                    </p>
                  </div>
                  <button
                    type="button"
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
            </div>

            {/* Root error */}
            {errors.root && (
              <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                {errors.root.message}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={isPending}
                className="flex flex-1 items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Salvando...
                  </>
                ) : isEditing ? (
                  'Salvar Alteracoes'
                ) : (
                  'Criar Certificado'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
