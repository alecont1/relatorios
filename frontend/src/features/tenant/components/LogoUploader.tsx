import { useRef, useState } from 'react'
import { Upload, Image } from 'lucide-react'
import { useLogoUploadUrl, useLogoConfirm } from '../api'

interface Props {
  label: string
  logoType: 'primary' | 'secondary'
  currentKey: string | null
  onUploadComplete: () => void
}

export function LogoUploader({ label, logoType, currentKey, onUploadComplete }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const getUploadUrl = useLogoUploadUrl()
  const confirmUpload = useLogoConfirm()

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/svg+xml', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      setError('Formato invalido. Use PNG, JPG, SVG ou WebP.')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Arquivo muito grande. Maximo 5MB.')
      return
    }

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
        <div className="flex h-20 w-20 items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50">
          {currentKey ? (
            <Image className="h-8 w-8 text-gray-400" />
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
        </div>
      </div>
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  )
}
