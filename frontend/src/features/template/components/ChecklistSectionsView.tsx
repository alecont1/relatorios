import { Camera, MessageSquare, Settings2 } from 'lucide-react'
import type { TemplateSection, TemplateField } from '../api/templateApi'

interface ChecklistSectionsViewProps {
  sections: TemplateSection[]
  onFieldClick: (field: TemplateField) => void
}

export function ChecklistSectionsView({
  sections,
  onFieldClick,
}: ChecklistSectionsViewProps) {
  if (!sections || sections.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        Nenhuma secao configurada. Importe um arquivo Excel para adicionar secoes.
      </div>
    )
  }

  const hasPhotoConfig = (field: TemplateField) => {
    return field.photo_config && (
      field.photo_config.required ||
      field.photo_config.min_count > 0 ||
      field.photo_config.require_gps
    )
  }

  const hasCommentConfig = (field: TemplateField) => {
    return field.comment_config?.enabled
  }

  return (
    <div className="space-y-4">
      {sections.map((section, sectionIdx) => (
        <div key={section.id || sectionIdx} className="rounded-lg border border-gray-200">
          {/* Section Header */}
          <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
            <h4 className="font-medium text-gray-900">
              {sectionIdx + 1}. {section.name}
            </h4>
            <p className="text-xs text-gray-500">{section.fields.length} campos</p>
          </div>

          {/* Fields */}
          <div className="divide-y divide-gray-100">
            {section.fields.map((field, fieldIdx) => (
              <button
                key={field.id || fieldIdx}
                type="button"
                onClick={() => field.id && onFieldClick(field)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-400 w-6">{fieldIdx + 1}.</span>
                  <div>
                    <span className="text-sm text-gray-900">{field.label}</span>
                    <span className="ml-2 text-xs text-gray-400">({field.field_type})</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {/* Photo indicator */}
                  {hasPhotoConfig(field) && (
                    <div className="flex items-center gap-1 text-blue-600" title="Foto configurada">
                      <Camera className="h-4 w-4" />
                      {field.photo_config?.min_count && field.photo_config.min_count > 0 && (
                        <span className="text-xs">{field.photo_config.min_count}+</span>
                      )}
                    </div>
                  )}

                  {/* Comment indicator */}
                  {hasCommentConfig(field) && (
                    <div className="text-green-600" title="Comentario habilitado">
                      <MessageSquare className="h-4 w-4" />
                    </div>
                  )}

                  {/* Configure button */}
                  <div className="text-gray-400 hover:text-gray-600">
                    <Settings2 className="h-4 w-4" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}

      <p className="text-xs text-gray-500 text-center">
        Clique em um campo para configurar fotos e comentarios
      </p>
    </div>
  )
}
