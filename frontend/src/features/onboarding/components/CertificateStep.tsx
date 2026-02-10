import { useForm } from 'react-hook-form'
import { Loader2, Plus, Award } from 'lucide-react'
import {
  useCreateCertificate,
  useCertificates,
  type CertificateCreate,
} from '@/features/certificate'

interface CertificateStepProps {
  onComplete: () => void
}

export function CertificateStep({ onComplete }: CertificateStepProps) {
  const createCertificate = useCreateCertificate()
  const { data: certificatesData } = useCertificates()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CertificateCreate>({
    defaultValues: {
      equipment_name: '',
      certificate_number: '',
      manufacturer: '',
      model: '',
      serial_number: '',
      laboratory: '',
      calibration_date: '',
      expiry_date: '',
    },
  })

  const certificates = certificatesData?.certificates || []

  const onSubmit = async (data: CertificateCreate) => {
    try {
      await createCertificate.mutateAsync(data)
      reset()
    } catch {
      // Error handled by mutation
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Certificados de Calibracao</h2>
        <p className="mt-1 text-sm text-gray-500">
          Cadastre os certificados de calibracao dos equipamentos de medicao
        </p>
      </div>

      {/* Existing certificates list */}
      {certificates.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">
            Certificados cadastrados ({certificates.length})
          </h3>
          <div className="divide-y rounded-lg border">
            {certificates.map((cert) => (
              <div key={cert.id} className="flex items-center gap-3 p-3">
                <Award className="h-5 w-5 text-blue-500" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{cert.equipment_name}</p>
                  <p className="text-xs text-gray-500">N. {cert.certificate_number}</p>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs ${
                  cert.status === 'valid' ? 'bg-green-100 text-green-700' :
                  cert.status === 'expiring' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {cert.status === 'valid' ? 'Valido' : cert.status === 'expiring' ? 'Vencendo' : 'Vencido'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Inline form */}
        <form onSubmit={handleSubmit(onSubmit)} className="onboarding-certificate-form space-y-4 rounded-lg border p-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Equipamento *</label>
              <input
                {...register('equipment_name', { required: 'Obrigatorio' })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="Ex: Megohmetro"
              />
              {errors.equipment_name && <p className="mt-1 text-xs text-red-600">{errors.equipment_name.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">N. Certificado *</label>
              <input
                {...register('certificate_number', { required: 'Obrigatorio' })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                placeholder="Ex: CAL-2026-001"
              />
              {errors.certificate_number && <p className="mt-1 text-xs text-red-600">{errors.certificate_number.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Fabricante</label>
              <input
                {...register('manufacturer')}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Modelo</label>
              <input
                {...register('model')}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">N. Serie</label>
              <input
                {...register('serial_number')}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Laboratorio</label>
              <input
                {...register('laboratory')}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Data Calibracao *</label>
              <input
                {...register('calibration_date', { required: 'Obrigatorio' })}
                type="date"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              {errors.calibration_date && <p className="mt-1 text-xs text-red-600">{errors.calibration_date.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Data Validade *</label>
              <input
                {...register('expiry_date', { required: 'Obrigatorio' })}
                type="date"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              />
              {errors.expiry_date && <p className="mt-1 text-xs text-red-600">{errors.expiry_date.message}</p>}
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createCertificate.isPending}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {createCertificate.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Adicionar Certificado
            </button>
          </div>
        </form>

      <div className="flex justify-start">
        <button
          onClick={onComplete}
          className="rounded-lg bg-green-600 px-6 py-2 text-white hover:bg-green-700"
        >
          Concluir Passo
        </button>
      </div>
    </div>
  )
}
