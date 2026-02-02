import { useState } from 'react'
import { X, FileText, AlertCircle } from 'lucide-react'
import type { Template } from '@/features/template/api/templateApi'
import type { CreateReportData } from '@/features/report/api/reportApi'

interface NewReportModalProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: CreateReportData) => void
  templates: Template[]
  isSubmitting: boolean
  error?: string
}

export function NewReportModal({
  isOpen,
  onClose,
  onSubmit,
  templates,
  isSubmitting,
  error,
}: NewReportModalProps) {
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [title, setTitle] = useState('')
  const [location, setLocation] = useState('')

  if (!isOpen) return null

  const selectedTemplate = templates.find((t) => t.id === selectedTemplateId)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedTemplateId || !title.trim()) return

    // Use a placeholder project ID for now (will be replaced with project selector)
    // In a real app, you'd have a project selector or get it from context
    const placeholderProjectId = '00000000-0000-0000-0000-000000000000'

    onSubmit({
      template_id: selectedTemplateId,
      project_id: placeholderProjectId,
      title: title.trim(),
      location: location.trim() || undefined,
    })
  }

  const handleClose = () => {
    if (!isSubmitting) {
      setSelectedTemplateId('')
      setTitle('')
      setLocation('')
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Novo Relatorio</h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="p-1 text-gray-400 hover:text-gray-600 rounded"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Error */}
          {error && (
            <div className="flex items-center gap-2 p-3 text-red-700 bg-red-50 rounded-lg">
              <AlertCircle className="h-5 w-5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Template Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template *
            </label>
            <select
              value={selectedTemplateId}
              onChange={(e) => setSelectedTemplateId(e.target.value)}
              required
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            >
              <option value="">Selecione um template...</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name} (v{template.version})
                </option>
              ))}
            </select>
          </div>

          {/* Template Info */}
          {selectedTemplate && (
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <FileText className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-900">{selectedTemplate.name}</p>
                <p className="text-blue-700">
                  Categoria: {selectedTemplate.category} | Codigo: {selectedTemplate.code}
                </p>
              </div>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Titulo do Relatorio *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Inspecao Bloco A - Janeiro 2026"
              required
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Localizacao (opcional)
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Ex: Edificio Central, 3o andar"
              disabled={isSubmitting}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !selectedTemplateId || !title.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Criando...' : 'Criar Relatorio'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
