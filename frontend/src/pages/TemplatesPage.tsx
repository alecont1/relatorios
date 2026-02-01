import { useState } from 'react'
import { Upload } from 'lucide-react'
import { TemplateList, ExcelUploader, TemplatePreviewModal } from '@/features/template/components'
import type { ExcelParseResponse, TemplateSection } from '@/features/template/api/templateApi'

export function TemplatesPage() {
  const [showUploader, setShowUploader] = useState(false)
  const [previewData, setPreviewData] = useState<{
    sections: TemplateSection[]
    errors?: string[]
    summary?: { section_count: number; field_count: number }
  } | null>(null)

  const handleParsed = (result: ExcelParseResponse) => {
    if (result.valid && result.sections) {
      setPreviewData({
        sections: result.sections,
        summary: result.summary,
      })
    } else {
      setPreviewData({
        sections: [],
        errors: result.errors,
      })
    }
    setShowUploader(false)
  }

  const handleClosePreview = () => {
    setPreviewData(null)
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
        <button
          onClick={() => setShowUploader(!showUploader)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Upload className="h-4 w-4" />
          Importar Excel
        </button>
      </div>

      {showUploader && (
        <div className="mb-6">
          <ExcelUploader onParsed={handleParsed} />
        </div>
      )}

      <TemplateList />

      {previewData && (
        <TemplatePreviewModal
          isOpen={true}
          onClose={handleClosePreview}
          sections={previewData.sections}
          errors={previewData.errors}
          summary={previewData.summary}
        />
      )}
    </div>
  )
}
