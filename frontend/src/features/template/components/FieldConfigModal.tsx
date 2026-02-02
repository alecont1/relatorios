import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Camera, MessageSquare, Loader2 } from 'lucide-react'
import {
  templateApi,
  type TemplateField,
  type PhotoConfig,
  type CommentConfig,
} from '../api/templateApi'

interface FieldConfigFormData {
  photo_required: boolean
  photo_min_count: number
  photo_max_count: number
  photo_require_gps: boolean
  photo_watermark: boolean
  comment_enabled: boolean
  comment_required: boolean
}

interface FieldConfigModalProps {
  field: TemplateField
  isOpen: boolean
  onClose: () => void
  onSave: () => void
}

export function FieldConfigModal({
  field,
  isOpen,
  onClose,
  onSave,
}: FieldConfigModalProps) {
  const queryClient = useQueryClient()

  const defaultPhotoConfig: PhotoConfig = {
    required: false,
    min_count: 0,
    max_count: 10,
    require_gps: false,
    watermark: true,
  }

  const defaultCommentConfig: CommentConfig = {
    enabled: true,
    required: false,
  }

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors },
    setError,
  } = useForm<FieldConfigFormData>({
    defaultValues: {
      photo_required: field.photo_config?.required ?? defaultPhotoConfig.required,
      photo_min_count: field.photo_config?.min_count ?? defaultPhotoConfig.min_count,
      photo_max_count: field.photo_config?.max_count ?? defaultPhotoConfig.max_count,
      photo_require_gps: field.photo_config?.require_gps ?? defaultPhotoConfig.require_gps,
      photo_watermark: field.photo_config?.watermark ?? defaultPhotoConfig.watermark,
      comment_enabled: field.comment_config?.enabled ?? defaultCommentConfig.enabled,
      comment_required: field.comment_config?.required ?? defaultCommentConfig.required,
    },
  })

  // Reset form when field changes
  useEffect(() => {
    reset({
      photo_required: field.photo_config?.required ?? defaultPhotoConfig.required,
      photo_min_count: field.photo_config?.min_count ?? defaultPhotoConfig.min_count,
      photo_max_count: field.photo_config?.max_count ?? defaultPhotoConfig.max_count,
      photo_require_gps: field.photo_config?.require_gps ?? defaultPhotoConfig.require_gps,
      photo_watermark: field.photo_config?.watermark ?? defaultPhotoConfig.watermark,
      comment_enabled: field.comment_config?.enabled ?? defaultCommentConfig.enabled,
      comment_required: field.comment_config?.required ?? defaultCommentConfig.required,
    })
  }, [field, reset])

  const updateMutation = useMutation({
    mutationFn: (data: { photo_config?: PhotoConfig; comment_config?: CommentConfig }) =>
      templateApi.updateFieldConfig(field.id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['template'] })
      onSave()
      onClose()
    },
  })

  const onSubmit = async (data: FieldConfigFormData) => {
    // Validate min <= max
    if (data.photo_min_count > data.photo_max_count) {
      setError('photo_min_count', {
        type: 'manual',
        message: 'Minimo nao pode ser maior que maximo',
      })
      return
    }

    const photo_config: PhotoConfig = {
      required: data.photo_required,
      min_count: data.photo_min_count,
      max_count: data.photo_max_count,
      require_gps: data.photo_require_gps,
      watermark: data.photo_watermark,
    }

    const comment_config: CommentConfig = {
      enabled: data.comment_enabled,
      required: data.comment_required,
    }

    await updateMutation.mutateAsync({ photo_config, comment_config })
  }

  const watchMinCount = watch('photo_min_count')
  const watchMaxCount = watch('photo_max_count')

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-lg rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Configurar Campo
            </h3>
            <p className="text-sm text-gray-500">{field.label}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-4 space-y-6">
          {/* Photo Settings */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Camera className="h-5 w-5 text-gray-600" />
              <h4 className="font-medium text-gray-900">Configuracao de Fotos</h4>
            </div>

            <div className="space-y-3 pl-7">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...register('photo_required')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Foto obrigatoria</span>
              </label>

              <div className="flex gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">
                    Minimo de fotos
                  </label>
                  <input
                    type="number"
                    {...register('photo_min_count', { valueAsNumber: true, min: 0, max: 20 })}
                    className="w-20 rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">
                    Maximo de fotos
                  </label>
                  <input
                    type="number"
                    {...register('photo_max_count', { valueAsNumber: true, min: 1, max: 20 })}
                    className="w-20 rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              {errors.photo_min_count && (
                <p className="text-xs text-red-600">{errors.photo_min_count.message}</p>
              )}
              {watchMinCount > watchMaxCount && (
                <p className="text-xs text-red-600">Minimo nao pode ser maior que maximo</p>
              )}

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...register('photo_require_gps')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Exigir GPS</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...register('photo_watermark')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Aplicar marca d'agua</span>
              </label>
            </div>
          </div>

          {/* Comment Settings */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="h-5 w-5 text-gray-600" />
              <h4 className="font-medium text-gray-900">Configuracao de Comentarios</h4>
            </div>

            <div className="space-y-3 pl-7">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...register('comment_enabled')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Permitir comentarios</span>
              </label>

              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  {...register('comment_required')}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Comentario obrigatorio</span>
              </label>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t border-gray-200 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit(onSubmit)}
            disabled={updateMutation.isPending || watchMinCount > watchMaxCount}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {updateMutation.isPending && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            Salvar
          </button>
        </div>
      </div>
    </div>
  )
}
