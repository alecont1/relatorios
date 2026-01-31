import { X } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateTenant } from '../api'

const schema = z.object({
  name: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  slug: z
    .string()
    .min(2, 'Slug deve ter pelo menos 2 caracteres')
    .regex(/^[a-z0-9-]+$/, 'Slug deve conter apenas letras minusculas, numeros e hifens'),
})

type FormData = z.infer<typeof schema>

interface Props {
  isOpen: boolean
  onClose: () => void
}

export function CreateTenantModal({ isOpen, onClose }: Props) {
  const createTenant = useCreateTenant()
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await createTenant.mutateAsync(data)
      reset()
      onClose()
    } catch (error) {
      // Error handled by React Query
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Novo Tenant</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Nome
            </label>
            <input
              {...register('name')}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="Nome da empresa"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Slug
            </label>
            <input
              {...register('slug')}
              className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
              placeholder="nome-da-empresa"
            />
            {errors.slug && (
              <p className="mt-1 text-sm text-red-500">{errors.slug.message}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Identificador unico. Apenas letras minusculas, numeros e hifens.
            </p>
          </div>

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-gray-600 hover:bg-gray-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createTenant.isPending}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {createTenant.isPending ? 'Criando...' : 'Criar'}
            </button>
          </div>

          {createTenant.error && (
            <p className="text-sm text-red-500">
              {(createTenant.error as Error).message || 'Erro ao criar tenant'}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
