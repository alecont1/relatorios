import { useRef, useEffect, useState, useCallback } from 'react'
import { X, RotateCcw, Check } from 'lucide-react'

interface SignaturePadProps {
  isOpen: boolean
  onClose: () => void
  onSave: (blob: Blob) => void
  roleName: string
  signerName?: string
  onSignerNameChange?: (name: string) => void
}

export function SignaturePad({
  isOpen,
  onClose,
  onSave,
  roleName,
  signerName = '',
  onSignerNameChange,
}: SignaturePadProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [hasSignature, setHasSignature] = useState(false)
  const [name, setName] = useState(signerName)

  // Initialize canvas
  useEffect(() => {
    if (!isOpen || !canvasRef.current || !containerRef.current) return

    const canvas = canvasRef.current
    const container = containerRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    // Set canvas size to match container
    const rect = container.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = 200 // Fixed height for signature area

    // Configure drawing style
    ctx.strokeStyle = '#1e293b' // slate-800
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    // Clear canvas with white background
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Add signature line
    ctx.beginPath()
    ctx.strokeStyle = '#e2e8f0' // slate-200
    ctx.lineWidth = 1
    ctx.moveTo(20, canvas.height - 40)
    ctx.lineTo(canvas.width - 20, canvas.height - 40)
    ctx.stroke()

    // Reset stroke style for drawing
    ctx.strokeStyle = '#1e293b'
    ctx.lineWidth = 2

    setHasSignature(false)
  }, [isOpen])

  const getCoordinates = useCallback(
    (e: React.MouseEvent | React.TouchEvent): { x: number; y: number } | null => {
      if (!canvasRef.current) return null

      const canvas = canvasRef.current
      const rect = canvas.getBoundingClientRect()

      if ('touches' in e) {
        const touch = e.touches[0]
        return {
          x: touch.clientX - rect.left,
          y: touch.clientY - rect.top,
        }
      }

      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      }
    },
    []
  )

  const startDrawing = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      const coords = getCoordinates(e)
      if (!coords || !canvasRef.current) return

      const ctx = canvasRef.current.getContext('2d')
      if (!ctx) return

      ctx.beginPath()
      ctx.moveTo(coords.x, coords.y)
      setIsDrawing(true)

      // Prevent scrolling on touch devices
      e.preventDefault()
    },
    [getCoordinates]
  )

  const draw = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      if (!isDrawing) return

      const coords = getCoordinates(e)
      if (!coords || !canvasRef.current) return

      const ctx = canvasRef.current.getContext('2d')
      if (!ctx) return

      ctx.lineTo(coords.x, coords.y)
      ctx.stroke()
      setHasSignature(true)

      // Prevent scrolling on touch devices
      e.preventDefault()
    },
    [isDrawing, getCoordinates]
  )

  const stopDrawing = useCallback(() => {
    setIsDrawing(false)
  }, [])

  const clearCanvas = useCallback(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear and redraw background
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Redraw signature line
    ctx.beginPath()
    ctx.strokeStyle = '#e2e8f0'
    ctx.lineWidth = 1
    ctx.moveTo(20, canvas.height - 40)
    ctx.lineTo(canvas.width - 20, canvas.height - 40)
    ctx.stroke()

    // Reset stroke style
    ctx.strokeStyle = '#1e293b'
    ctx.lineWidth = 2

    setHasSignature(false)
  }, [])

  const handleSave = useCallback(() => {
    if (!canvasRef.current || !hasSignature) return

    canvasRef.current.toBlob(
      (blob) => {
        if (blob) {
          onSignerNameChange?.(name)
          onSave(blob)
        }
      },
      'image/png',
      1.0
    )
  }, [hasSignature, name, onSave, onSignerNameChange])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Assinatura</h2>
            <p className="text-sm text-gray-500">{roleName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Signer name input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome do assinante
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Digite o nome completo"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Signature canvas */}
          <div ref={containerRef} className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Assine abaixo
            </label>
            <canvas
              ref={canvasRef}
              className="w-full border border-gray-300 rounded-lg cursor-crosshair touch-none"
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchMove={draw}
              onTouchEnd={stopDrawing}
            />
            <p className="text-xs text-gray-400 mt-1 text-center">
              Use o mouse ou dedo para assinar
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50 rounded-b-xl">
          <button
            onClick={clearCanvas}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RotateCcw className="h-4 w-4" />
            Limpar
          </button>
          <button
            onClick={handleSave}
            disabled={!hasSignature}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="h-4 w-4" />
            Confirmar
          </button>
        </div>
      </div>
    </div>
  )
}
