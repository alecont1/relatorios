import {
  ChevronDown,
  ChevronUp,
  MessageSquare,
} from 'lucide-react'
import type {
  SnapshotSection,
  SnapshotField,
} from '@/features/report/api/reportApi'
import {
  PhotoGallery,
  type PhotoMetadata,
} from '@/features/photo'

interface ChecklistStepProps {
  sections: SnapshotSection[]
  responses: Record<string, { value: string; comment: string }>
  onResponseChange: (fieldKey: string, value: string) => void
  onCommentChange: (fieldKey: string, comment: string) => void
  expandedSections: Set<string>
  onToggleSection: (sectionId: string) => void
  showComments: Set<string>
  onToggleComment: (fieldKey: string) => void
  isReadOnly: boolean
  photos: Record<string, PhotoMetadata[]>
  getResponseId: (fieldId: string | undefined, sectionName: string, fieldLabel: string) => string | undefined
  onOpenCamera: (responseId: string) => void
  onDeletePhoto: (responseId: string, photoId: string) => void
}

export function ChecklistStep({
  sections,
  responses,
  onResponseChange,
  onCommentChange,
  expandedSections,
  onToggleSection,
  showComments,
  onToggleComment,
  isReadOnly,
  photos,
  getResponseId,
  onOpenCamera,
  onDeletePhoto,
}: ChecklistStepProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Checklist</h2>
      {sections.map((section) => (
        <SectionAccordion
          key={section.id}
          section={section}
          isExpanded={expandedSections.has(section.id)}
          onToggle={() => onToggleSection(section.id)}
          responses={responses}
          onResponseChange={(fieldKey, value) => onResponseChange(fieldKey, value)}
          onCommentChange={onCommentChange}
          showComments={showComments}
          onToggleComment={onToggleComment}
          isReadOnly={isReadOnly}
          photos={photos}
          getResponseId={getResponseId}
          onOpenCamera={onOpenCamera}
          onDeletePhoto={onDeletePhoto}
        />
      ))}
    </div>
  )
}

// --- SectionAccordion ---

interface SectionAccordionProps {
  section: SnapshotSection
  isExpanded: boolean
  onToggle: () => void
  responses: Record<string, { value: string; comment: string }>
  onResponseChange: (fieldKey: string, value: string) => void
  onCommentChange: (fieldKey: string, comment: string) => void
  showComments: Set<string>
  onToggleComment: (fieldKey: string) => void
  isReadOnly: boolean
  photos: Record<string, PhotoMetadata[]>
  getResponseId: (fieldId: string | undefined, sectionName: string, fieldLabel: string) => string | undefined
  onOpenCamera: (responseId: string) => void
  onDeletePhoto: (responseId: string, photoId: string) => void
}

function SectionAccordion({
  section,
  isExpanded,
  onToggle,
  responses,
  onResponseChange,
  onCommentChange,
  showComments,
  onToggleComment,
  isReadOnly,
  photos,
  getResponseId,
  onOpenCamera,
  onDeletePhoto,
}: SectionAccordionProps) {
  const filledCount = section.fields.filter((f) => {
    const key = f.id || `${section.name}:${f.label}`
    return responses[key]?.value
  }).length

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
      >
        <div className="flex items-center gap-3">
          <span className="font-medium text-gray-900">{section.name}</span>
          <span className="text-sm text-gray-500">
            {filledCount}/{section.fields.length} campos
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="border-t divide-y">
          {section.fields.map((field) => {
            const responseId = getResponseId(field.id, section.name, field.label)
            const fieldKey = field.id || `${section.name}:${field.label}`
            return (
              <FieldRow
                key={field.id}
                field={field}
                response={responses[fieldKey] || { value: '', comment: '' }}
                onValueChange={(value) => onResponseChange(fieldKey, value)}
                onCommentChange={(comment) => onCommentChange(fieldKey, comment)}
                showComment={showComments.has(fieldKey)}
                onToggleComment={() => onToggleComment(fieldKey)}
                isReadOnly={isReadOnly}
                photos={responseId ? photos[responseId] || [] : []}
                responseId={responseId}
                onOpenCamera={onOpenCamera}
                onDeletePhoto={onDeletePhoto}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

// --- FieldRow ---

interface FieldRowProps {
  field: SnapshotField
  response: { value: string; comment: string }
  onValueChange: (value: string) => void
  onCommentChange: (comment: string) => void
  showComment: boolean
  onToggleComment: () => void
  isReadOnly: boolean
  photos: PhotoMetadata[]
  responseId?: string
  onOpenCamera: (responseId: string) => void
  onDeletePhoto: (responseId: string, photoId: string) => void
}

function FieldRow({
  field,
  response,
  onValueChange,
  onCommentChange,
  showComment,
  onToggleComment,
  isReadOnly,
  photos,
  responseId,
  onOpenCamera,
  onDeletePhoto,
}: FieldRowProps) {
  const hasCommentConfig = field.comment_config?.enabled
  const photoConfig = field.photo_config
  const hasPhotoConfig = photoConfig && (photoConfig.required || (photoConfig.min_count || 0) > 0 || (photoConfig.max_count || 0) > 0)

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className="text-sm text-gray-900">{field.label}</p>
        </div>

        <div className="flex items-center gap-2">
          <FieldInput
            field={field}
            value={response.value}
            onChange={onValueChange}
            isReadOnly={isReadOnly}
          />

          {hasCommentConfig && !isReadOnly && (
            <button
              onClick={onToggleComment}
              className={`p-2 rounded ${
                showComment || response.comment
                  ? 'bg-blue-100 text-blue-600'
                  : 'bg-gray-100 text-gray-400 hover:text-gray-600'
              }`}
              title="Adicionar comentario"
            >
              <MessageSquare className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {(showComment || response.comment) && hasCommentConfig && (
        <div>
          <textarea
            value={response.comment}
            onChange={(e) => onCommentChange(e.target.value)}
            placeholder="Adicione um comentario..."
            disabled={isReadOnly}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
          />
        </div>
      )}

      {(hasPhotoConfig || photos.length > 0) && responseId && (
        <PhotoGallery
          photos={photos}
          maxPhotos={photoConfig?.max_count}
          required={photoConfig?.required || (photoConfig?.min_count || 0) > 0}
          onAddPhoto={() => onOpenCamera(responseId)}
          onDeletePhoto={(photoId) => onDeletePhoto(responseId, photoId)}
          isReadOnly={isReadOnly}
        />
      )}
    </div>
  )
}

// --- FieldInput ---

interface FieldInputProps {
  field: SnapshotField
  value: string
  onChange: (value: string) => void
  isReadOnly: boolean
}

function FieldInput({ field, value, onChange, isReadOnly }: FieldInputProps) {
  const options = field.options
    ? field.options.split(/[,\/]/).map((o) => o.trim()).filter(Boolean)
    : []

  switch (field.field_type) {
    case 'dropdown':
      return (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isReadOnly}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 min-w-[150px]"
        >
          <option value="">Selecione...</option>
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      )

    case 'checkbox':
      return (
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'Sim'}
              onChange={() => onChange('Sim')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">Sim</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'Nao'}
              onChange={() => onChange('Nao')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">Nao</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name={field.id}
              checked={value === 'N/A'}
              onChange={() => onChange('N/A')}
              disabled={isReadOnly}
              className="h-4 w-4 text-blue-600"
            />
            <span className="text-sm">N/A</span>
          </label>
        </div>
      )

    case 'text':
    default:
      return (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isReadOnly}
          placeholder="Digite..."
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 min-w-[200px]"
        />
      )
  }
}
