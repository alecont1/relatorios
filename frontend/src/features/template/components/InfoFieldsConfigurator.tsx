import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, GripVertical, Save, Loader2 } from 'lucide-react'
import { templateApi, type InfoField, type InfoFieldCreate } from '../api/templateApi'

interface InfoFieldFormData {
  fields: Array<{
    id?: string
    label: string
    field_type: 'text' | 'date' | 'select'
    options: string
    required: boolean
    isNew?: boolean
  }>
}

interface InfoFieldsConfiguratorProps {
  templateId: string
  initialFields: InfoField[]
  onUpdate: () => void
}

export function InfoFieldsConfigurator({
  templateId,
  initialFields,
  onUpdate,
}: InfoFieldsConfiguratorProps) {
  const [isSaving, setIsSaving] = useState(false)
  const queryClient = useQueryClient()

  const { control, register, watch, handleSubmit } = useForm<InfoFieldFormData>({
    defaultValues: {
      fields: initialFields.map((f) => ({
        id: f.id,
        label: f.label,
        field_type: f.field_type,
        options: f.options?.join(', ') || '',
        required: f.required,
        isNew: false,
      })),
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'fields',
    keyName: 'key',
  })

  const createMutation = useMutation({
    mutationFn: (data: InfoFieldCreate) => templateApi.createInfoField(templateId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['infoFields', templateId] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ fieldId, data }: { fieldId: string; data: Partial<InfoFieldCreate> }) =>
      templateApi.updateInfoField(templateId, fieldId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['infoFields', templateId] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (fieldId: string) => templateApi.deleteInfoField(templateId, fieldId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['infoFields', templateId] })
    },
  })

  const handleAddField = () => {
    append({
      label: '',
      field_type: 'text',
      options: '',
      required: true,
      isNew: true,
    })
  }

  const handleRemoveField = async (index: number) => {
    const field = fields[index]
    if (field.id && !field.isNew) {
      await deleteMutation.mutateAsync(field.id)
    }
    remove(index)
    onUpdate()
  }

  const onSubmit = async (data: InfoFieldFormData) => {
    setIsSaving(true)
    try {
      for (const field of data.fields) {
        const options = field.field_type === 'select' && field.options
          ? field.options.split(',').map((o) => o.trim()).filter(Boolean)
          : undefined

        const fieldData: InfoFieldCreate = {
          label: field.label,
          field_type: field.field_type,
          required: field.required,
          ...(options && options.length > 0 ? { options } : {}),
        }

        if (field.isNew || !field.id) {
          await createMutation.mutateAsync(fieldData)
        } else {
          await updateMutation.mutateAsync({ fieldId: field.id, data: fieldData })
        }
      }
      onUpdate()
    } catch (error) {
      console.error('Error saving info fields:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const watchFields = watch('fields')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {fields.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          Nenhum campo de informacao configurado
        </div>
      ) : (
        <div className="space-y-3">
          {fields.map((field, index) => (
            <div
              key={field.key}
              className="flex items-start gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3"
            >
              <div className="mt-2 cursor-move text-gray-400">
                <GripVertical className="h-5 w-5" />
              </div>

              <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Label */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Label
                  </label>
                  <input
                    {...register(`fields.${index}.label`)}
                    placeholder="Nome do campo"
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  />
                </div>

                {/* Type */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Tipo
                  </label>
                  <select
                    {...register(`fields.${index}.field_type`)}
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  >
                    <option value="text">Texto</option>
                    <option value="date">Data</option>
                    <option value="select">Selecao</option>
                  </select>
                </div>

                {/* Options (only for select) */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Opcoes
                  </label>
                  <input
                    {...register(`fields.${index}.options`)}
                    placeholder="Opcao1, Opcao2, Opcao3"
                    disabled={watchFields[index]?.field_type !== 'select'}
                    className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100 disabled:text-gray-400"
                  />
                </div>

                {/* Required */}
                <div className="flex items-end">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      {...register(`fields.${index}.required`)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    Obrigatorio
                  </label>
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleRemoveField(index)}
                className="mt-6 text-red-500 hover:text-red-700"
                title="Remover campo"
              >
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={handleAddField}
          className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <Plus className="h-4 w-4" />
          Adicionar Campo
        </button>

        <button
          type="submit"
          disabled={isSaving}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isSaving ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          Salvar Alteracoes
        </button>
      </div>
    </form>
  )
}
