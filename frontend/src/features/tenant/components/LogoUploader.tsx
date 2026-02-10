import { useRef, useState, useEffect } from 'react'
import { Upload } from 'lucide-react'
import { useLogoUploadUrl, useLogoConfirm } from '../api'
import { getLogoUrl } from '../types'

interface Props {
  label: string
  logoType: 'primary' | 'secondary'
  currentKey: string | null
  onUploadComplete: () => void
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_WIDTH = 800
const MAX_HEIGHT = 400

function validateDimensions(file: File): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    // SVG files don't need dimension validation
    if (file.type === 'image/svg+xml') {
      resolve({ width: 0, height: 0 })
      return
    }
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(img.src)
      if (img.width > MAX_WIDTH || img.height > MAX_HEIGHT) {
        reject(new Error(`Dimensoes ${img.width}x${img.height}px excedem o maximo recomendado de ${MAX_WIDTH}x${MAX_HEIGHT}px.`))
      } else {
        resolve({ width: img.width, height: img.height })
      }
    }
    img.onerror = () => {
      URL.revokeObjectURL(img.src)
      reject(new Error('Nao foi possivel ler a imagem.'))
    }
    img.src = URL.createObjectURL(file)
  })
}

export function LogoUploader({ label, logoType, currentKey, onUploadComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const getUploadUrl = useLogoUploadUrl()
  const confirmUpload = useLogoConfirm()

  // Build preview from currentKey (R2 public URL) or local blob
  useEffect(() => {
    const url = getLogoUrl(currentKey)
    if (url) {
      setPreviewUrl(url)
    }
  }, [currentKey])

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError('Formato invalido. Use PNG, JPG, SVG ou WebP.')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > MAX_FILE_SIZE) {
      setError('Arquivo muito grande. Maximo 10MB.')
      return
    }

    // Validate dimensions
    try {
      await validateDimensions(file)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao validar dimensoes.')
      return
    }

    // Show local preview immediately
    const localPreview = URL.createObjectURL(file)
    setPreviewUrl(localPreview)

    setError(null)
    setIsUploading(true)

    try {
      // Get presigned URL
      const { upload_url, object_key } = await getUploadUrl.mutateAsync({
        logo_type: logoType,
        filename: file.name,
      })

      // Upload to R2
      const response = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      })

      // Verify upload succeeded (HTTP 200 from presigned URL)
      if (!response.ok) {
        throw new Error(`Falha no upload: ${response.status}`)
      }

      // Confirm upload
      await confirmUpload.mutateAsync({
        logo_type: logoType,
        object_key,
      })

      onUploadComplete()
    } catch (err) {
      setError('Erro ao enviar logo')
      // Revert preview to R2 URL on error
      const r2Url = getLogoUrl(currentKey)
      setPreviewUrl(r2Url ?? null)
    } finally {
      setIsUploading(false)
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="mt-2 flex items-center gap-4">
        <div className="flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 overflow-hidden"
          style={{ width: 160, height: 80 }}
        >
          {previewUrl ? (
            <img
              src={previewUrl}
              alt={`Preview ${logoType}`}
              className="max-w-full max-h-full object-contain"
            />
          ) : (
            <Upload className="h-8 w-8 text-gray-400" />
          )}
        </div>
        <div>
          <input
            ref={inputRef}
            type="file"
            accept="image/png,image/jpeg,image/svg+xml,image/webp"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            disabled={isUploading}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            {isUploading ? 'Enviando...' : currentKey ? 'Alterar' : 'Selecionar'}
          </button>
          {currentKey && (
            <p className="mt-1 text-xs text-green-600">Logo configurada</p>
          )}
          <p className="mt-1 text-xs text-gray-400">
            Max 10MB, {MAX_WIDTH}x{MAX_HEIGHT}px
          </p>
        </div>
      </div>
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  )
}
