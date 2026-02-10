import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Loader2 } from 'lucide-react'
import { type Certificate } from '../api/certificateApi'
import { useCreateCertificate, useUpdateCertificate } from '../hooks/useCertificates'

const certificateSchema = z.object({
  equipment_name: z.string().min(1, 'Nome do equipamento e obrigatorio'),
  certificate_number: z.string().min(1, 'Numero do certificado e obrigatorio'),
  manufacturer: z.string().optional(),
  model: z.string().optional(),
  serial_number: z.string().optional(),
  laboratory: z.string().optional(),
  calibration_date: z.string().min(1, 'Data de calibracao e obrigatoria'),
  expiry_date: z.string().min(1, 'Data de validade e obrigatoria'),
  status: z.enum(['valid', 'expiring', 'expired']).optional(),
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
      certificate_number: '',
      manufacturer: '',
      model: '',
      serial_number: '',
      laboratory: '',
      calibration_date: '',
      expiry_date: '',
      status: 'valid',
    },
  })

  // Reset form when certificate changes or modal opens
  useEffect(() => {
    if (isOpen) {
      if (certificate) {
        reset({
          equipment_name: certificate.equipment_name,
          certificate_number: certificate.certificate_number,
          manufacturer: certificate.manufacturer || '',
          model: certificate.model || '',
          serial_number: certificate.serial_number || '',
          laboratory: certificate.laboratory || '',
          calibration_date: certificate.calibration_date,
          expiry_date: certificate.expiry_date,
          status: certificate.status,
        })
      } else {
        reset({
          equipment_name: '',
          certificate_number: '',
          manufacturer: '',
          model: '',
          serial_number: '',
          laboratory: '',
          calibration_date: '',
          expiry_date: '',
          status: 'valid',
        })
      }
    }
  }, [isOpen, certificate, reset])

  const onSubmit = async (data: CertificateFormData) => {
    try {
      if (isEditing && certificate) {
        await updateMutation.mutateAsync({ id: certificate.id, data })
      } else {
        await createMutation.mutateAsync(data)
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

  const isPending = isSubmitting || createMutation.isPending || updateMutation.isPending

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

            {/* Certificate Number */}
            <div>
              <label
                htmlFor="certificate_number"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Numero do Certificado *
              </label>
              <input
                {...register('certificate_number')}
                type="text"
                id="certificate_number"
                placeholder="Ex: CAL-2024-001"
                className={`block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${errors.certificate_number ? 'border-red-500' : ''}`}
              />
              {errors.certificate_number && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.certificate_number.message}
                </p>
              )}
            </div>

            {/* Manufacturer & Model */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="manufacturer"
                  className="mb-1 block text-sm font-medium text-gray-700"
                >
                  Fabricante
                </label>
                <input
                  {...register('manufacturer')}
                  type="text"
                  id="manufacturer"
                  placeholder="Ex: Fluke"
                  className="block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>

              <div>
                <label
                  htmlFor="model"
                  className="mb-1 block text-sm font-medium text-gray-700"
                >
                  Modelo
                </label>
                <input
                  {...register('model')}
                  type="text"
                  id="model"
                  placeholder="Ex: 87V"
                  className="block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            {/* Serial Number */}
            <div>
              <label
                htmlFor="serial_number"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Numero de Serie
              </label>
              <input
                {...register('serial_number')}
                type="text"
                id="serial_number"
                placeholder="Ex: SN-12345678"
                className="block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Laboratory */}
            <div>
              <label
                htmlFor="laboratory"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Laboratorio
              </label>
              <input
                {...register('laboratory')}
                type="text"
                id="laboratory"
                placeholder="Ex: Laboratorio ABC Calibracoes"
                className="block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label
                  htmlFor="calibration_date"
                  className="mb-1 block text-sm font-medium text-gray-700"
                >
                  Data de Calibracao *
                </label>
                <input
                  {...register('calibration_date')}
                  type="date"
                  id="calibration_date"
                  className={`block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${errors.calibration_date ? 'border-red-500' : ''}`}
                />
                {errors.calibration_date && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.calibration_date.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="expiry_date"
                  className="mb-1 block text-sm font-medium text-gray-700"
                >
                  Data de Validade *
                </label>
                <input
                  {...register('expiry_date')}
                  type="date"
                  id="expiry_date"
                  className={`block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${errors.expiry_date ? 'border-red-500' : ''}`}
                />
                {errors.expiry_date && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.expiry_date.message}
                  </p>
                )}
              </div>
            </div>

            {/* Status */}
            <div>
              <label
                htmlFor="status"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Status
              </label>
              <select
                {...register('status')}
                id="status"
                className="block w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              >
                <option value="valid">Valido</option>
                <option value="expiring">Vencendo</option>
                <option value="expired">Vencido</option>
              </select>
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
