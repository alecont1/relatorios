import { useState } from 'react'
import { X, Check, AlertTriangle, ChevronDown, ChevronRight } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { TemplateSection, TemplateCreateData } from '../api/templateApi'
import { templateApi } from '../api/templateApi'

interface TemplatePreviewModalProps {
  isOpen: boolean
  onClose: () => void
  sections: TemplateSection[]
  errors?: string[]
  summary?: { section_count: number; field_count: number }
}

const CATEGORIES = ['Commissioning', 'Inspection', 'Maintenance', 'Testing'] as const

export function TemplatePreviewModal({
  isOpen,
  onClose,
  sections,
  errors,
  summary,
}: TemplatePreviewModalProps) {
  const [name, setName] = useState('')
  const [category, setCategory] = useState<typeof CATEGORIES[number]>('Commissioning')
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set([0]))
  const queryClient = useQueryClient()

  const createMutation = useMutation({
    mutationFn: templateApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      onClose()
      setName('')
    },
  })

  const toggleSection = (index: number) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  const handleConfirm = () => {
    if (!name.trim()) return

    const data: TemplateCreateData = {
      name: name.trim(),
      category,
      sections: sections.map((s, i) => ({
        name: s.name,
        order: i,
        fields: s.fields.map((f, j) => ({
          label: f.label,
          field_type: f.field_type,
          options: f.options,
          order: j,
        })),
      })),
    }

    createMutation.mutate(data)
  }

  if (!isOpen) return null

  const hasErrors = errors && errors.length > 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-lg font-semibold">
            {hasErrors ? 'Erros de Validacao' : 'Preview do Template'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="max-h-[60vh] overflow-y-auto p-6">
          {hasErrors ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
                <span className="font-medium">
                  Encontrados {errors.length} erro(s) no arquivo
                </span>
              </div>
              <ul className="ml-7 list-disc space-y-1 text-sm text-red-600">
                {errors.map((error, i) => (
                  <li key={i}>{error}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Summary */}
              {summary && (
                <div className="rounded-lg bg-green-50 p-4 text-green-800">
                  <div className="flex items-center gap-2">
                    <Check className="h-5 w-5" />
                    <span className="font-medium">Arquivo valido!</span>
                  </div>
                  <p className="mt-1 text-sm">
                    {summary.section_count} secao(oes) com {summary.field_count} campo(s)
                  </p>
                </div>
              )}

              {/* Template metadata */}
              <div className="space-y-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Nome do Template *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Ex: Commissioning Report v1"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Categoria *
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as typeof category)}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Sections preview */}
              <div className="space-y-2">
                <h3 className="font-medium text-gray-700">Secoes e Campos</h3>
                {sections.map((section, sectionIndex) => (
                  <div key={sectionIndex} className="rounded border border-gray-200">
                    <button
                      onClick={() => toggleSection(sectionIndex)}
                      className="flex w-full items-center justify-between px-4 py-2 hover:bg-gray-50"
                    >
                      <span className="font-medium">{section.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">
                          {section.fields.length} campo(s)
                        </span>
                        {expandedSections.has(sectionIndex) ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </div>
                    </button>
                    {expandedSections.has(sectionIndex) && (
                      <div className="border-t bg-gray-50 px-4 py-2">
                        <ul className="space-y-1 text-sm">
                          {section.fields.map((field, fieldIndex) => (
                            <li key={fieldIndex} className="flex items-center gap-2">
                              <span className="text-gray-600">{field.label}</span>
                              <span className={`rounded px-1.5 py-0.5 text-xs ${
                                field.field_type === 'dropdown'
                                  ? 'bg-blue-100 text-blue-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {field.field_type}
                              </span>
                              {field.options && (
                                <span className="text-xs text-gray-400">
                                  ({field.options.join(', ')})
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 border-t px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-lg border border-gray-300 px-4 py-2 hover:bg-gray-50"
          >
            {hasErrors ? 'Fechar' : 'Cancelar'}
          </button>
          {!hasErrors && (
            <button
              onClick={handleConfirm}
              disabled={!name.trim() || createMutation.isPending}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Salvando...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4" />
                  Confirmar e Criar
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
