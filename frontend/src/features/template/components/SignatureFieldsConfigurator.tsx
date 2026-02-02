import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, GripVertical, Save, Loader2 } from 'lucide-react'
import { templateApi, type SignatureField, type SignatureFieldCreate } from '../api/templateApi'

interface SignatureFieldFormData {
  fields: Array<{
    id?: string
    role_name: string
    required: boolean
    isNew?: boolean
  }>
}

interface SignatureFieldsConfiguratorProps {
  templateId: string
  initialFields: SignatureField[]
  onUpdate: () => void
}

const COMMON_ROLES = [
  'Tecnico Executor',
  'Responsavel Tecnico',
  'Cliente',
  'Supervisor',
  'Inspetor',
]

export function SignatureFieldsConfigurator({
  templateId,
  initialFields,
  onUpdate,
}: SignatureFieldsConfiguratorProps) {
  const [isSaving, setIsSaving] = useState(false)
  const queryClient = useQueryClient()

  const { control, register, handleSubmit } = useForm<SignatureFieldFormData>({
    defaultValues: {
      fields: initialFields.map((f) => ({
        id: f.id,
        role_name: f.role_name,
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
    mutationFn: (data: SignatureFieldCreate) =>
      templateApi.createSignatureField(templateId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['signatureFields', templateId] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({
      fieldId,
      data,
    }: {
      fieldId: string
      data: Partial<SignatureFieldCreate>
    }) => templateApi.updateSignatureField(templateId, fieldId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['signatureFields', templateId] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (fieldId: string) =>
      templateApi.deleteSignatureField(templateId, fieldId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['signatureFields', templateId] })
    },
  })

  const handleAddField = (roleName: string = '') => {
    append({
      role_name: roleName,
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

  const onSubmit = async (data: SignatureFieldFormData) => {
    setIsSaving(true)
    try {
      for (const field of data.fields) {
        const fieldData: SignatureFieldCreate = {
          role_name: field.role_name,
          required: field.required,
        }

        if (field.isNew || !field.id) {
          await createMutation.mutateAsync(fieldData)
        } else {
          await updateMutation.mutateAsync({ fieldId: field.id, data: fieldData })
        }
      }
      onUpdate()
    } catch (error) {
      console.error('Error saving signature fields:', error)
    } finally {
      setIsSaving(false)
    }
  }

  // Get unused common roles for quick add
  const usedRoles = fields.map((f) => f.role_name)
  const availableRoles = COMMON_ROLES.filter((r) => !usedRoles.includes(r))

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {fields.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          Nenhum campo de assinatura configurado
        </div>
      ) : (
        <div className="space-y-3">
          {fields.map((field, index) => (
            <div
              key={field.key}
              className="flex items-center gap-3 rounded-lg border border-gray-200 bg-gray-50 p-3"
            >
              <div className="cursor-move text-gray-400">
                <GripVertical className="h-5 w-5" />
              </div>

              <div className="flex-1">
                <input
                  {...register(`fields.${index}.role_name`)}
                  placeholder="Nome do cargo (ex: Tecnico Executor)"
                  className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>

              <label className="flex items-center gap-2 text-sm whitespace-nowrap">
                <input
                  type="checkbox"
                  {...register(`fields.${index}.required`)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                Obrigatorio
              </label>

              <button
                type="button"
                onClick={() => handleRemoveField(index)}
                className="text-red-500 hover:text-red-700"
                title="Remover assinatura"
              >
                <Trash2 className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Quick add suggestions */}
      {availableRoles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-500">Adicionar:</span>
          {availableRoles.map((role) => (
            <button
              key={role}
              type="button"
              onClick={() => handleAddField(role)}
              className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-100"
            >
              + {role}
            </button>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={() => handleAddField()}
          className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <Plus className="h-4 w-4" />
          Adicionar Assinatura
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
