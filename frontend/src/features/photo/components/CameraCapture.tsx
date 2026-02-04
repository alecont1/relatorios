import { useState, useRef, useEffect, useCallback } from 'react'
import {
  Camera,
  X,
  RefreshCw,
  MapPin,
  Loader2,
  Check,
  AlertCircle,
} from 'lucide-react'
import { useCamera } from '../hooks/useCamera'
import { useGeolocation, type GPSCoordinates } from '../hooks/useGeolocation'
import { processImage } from '../utils/imageProcessor'

interface CameraCaptureProps {
  isOpen: boolean
  onClose: () => void
  onCapture: (blob: Blob, metadata: CaptureMetadata) => void
  tenantLogo?: string
  projectName?: string
  watermarkText?: string
  requireGPS?: boolean
}

export interface CaptureMetadata {
  capturedAt: Date
  gps?: GPSCoordinates
  address?: string
}

export function CameraCapture({
  isOpen,
  onClose,
  onCapture,
  tenantLogo,
  projectName,
  watermarkText,
  requireGPS = false,
}: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [capturedImage, setCapturedImage] = useState<Blob | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [address, setAddress] = useState<string | null>(null)

  const camera = useCamera({ facingMode: 'environment' })
  const geolocation = useGeolocation({ enableHighAccuracy: true })

  // Start camera when modal opens
  useEffect(() => {
    if (isOpen && videoRef.current) {
      camera.startCamera(videoRef.current)
      geolocation.getCurrentPosition()
    }

    return () => {
      camera.stopCamera()
    }
  }, [isOpen])

  // Reverse geocode when GPS is obtained
  useEffect(() => {
    if (geolocation.coordinates && !address) {
      reverseGeocode(geolocation.coordinates).then(setAddress)
    }
  }, [geolocation.coordinates, address])

  const handleCapture = useCallback(async () => {
    if (requireGPS && !geolocation.coordinates) {
      return // Wait for GPS
    }

    const blob = await camera.capturePhoto()
    if (blob) {
      setCapturedImage(blob)
    }
  }, [camera, requireGPS, geolocation.coordinates])

  const handleConfirm = useCallback(async () => {
    if (!capturedImage) return

    setIsProcessing(true)
    try {
      // Process image with watermark
      const processed = await processImage(capturedImage, {
        timestamp: new Date(),
        address: address || undefined,
        tenantLogo,
        projectName,
        watermarkText,
      })

      onCapture(processed, {
        capturedAt: new Date(),
        gps: geolocation.coordinates || undefined,
        address: address || undefined,
      })

      // Reset state
      setCapturedImage(null)
      onClose()
    } catch (error) {
      console.error('Error processing image:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [capturedImage, address, tenantLogo, projectName, watermarkText, geolocation.coordinates, onCapture, onClose])

  const handleRetake = useCallback(() => {
    setCapturedImage(null)
  }, [])

  const handleClose = useCallback(() => {
    camera.stopCamera()
    setCapturedImage(null)
    setAddress(null)
    onClose()
  }, [camera, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 text-white">
        <button onClick={handleClose} className="p-2">
          <X className="h-6 w-6" />
        </button>

        <div className="flex items-center gap-2">
          {/* GPS Status */}
          {geolocation.isLoading ? (
            <span className="flex items-center gap-1 text-sm text-yellow-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Obtendo GPS...
            </span>
          ) : geolocation.coordinates ? (
            <span className="flex items-center gap-1 text-sm text-green-400">
              <MapPin className="h-4 w-4" />
              GPS OK ({geolocation.coordinates.accuracy.toFixed(0)}m)
            </span>
          ) : geolocation.error ? (
            <span className="flex items-center gap-1 text-sm text-red-400">
              <AlertCircle className="h-4 w-4" />
              {geolocation.error}
            </span>
          ) : null}
        </div>

        {!capturedImage && (
          <button onClick={() => camera.switchCamera()} className="p-2">
            <RefreshCw className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Camera Preview / Captured Image */}
      <div className="flex-1 relative">
        {!capturedImage ? (
          <video
            ref={videoRef}
            className="absolute inset-0 w-full h-full object-cover"
            playsInline
            muted
          />
        ) : (
          <img
            src={URL.createObjectURL(capturedImage)}
            alt="Captured"
            className="absolute inset-0 w-full h-full object-contain"
          />
        )}

        {/* Error overlay */}
        {camera.error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/80">
            <div className="text-center text-white p-4">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 text-red-400" />
              <p className="text-lg">{camera.error}</p>
              <button
                onClick={handleClose}
                className="mt-4 px-4 py-2 bg-white text-black rounded-lg"
              >
                Fechar
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Address display */}
      {address && (
        <div className="bg-black/60 text-white text-sm p-2 text-center">
          <MapPin className="h-4 w-4 inline mr-1" />
          {address}
        </div>
      )}

      {/* Controls */}
      <div className="p-6 flex justify-center gap-6">
        {!capturedImage ? (
          <button
            onClick={handleCapture}
            disabled={requireGPS && !geolocation.coordinates}
            className="w-20 h-20 rounded-full bg-white flex items-center justify-center disabled:opacity-50"
          >
            <Camera className="h-8 w-8 text-black" />
          </button>
        ) : (
          <>
            <button
              onClick={handleRetake}
              disabled={isProcessing}
              className="w-16 h-16 rounded-full bg-gray-600 flex items-center justify-center"
            >
              <RefreshCw className="h-6 w-6 text-white" />
            </button>
            <button
              onClick={handleConfirm}
              disabled={isProcessing}
              className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center"
            >
              {isProcessing ? (
                <Loader2 className="h-8 w-8 text-white animate-spin" />
              ) : (
                <Check className="h-8 w-8 text-white" />
              )}
            </button>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * Reverse geocode coordinates to address.
 * Uses OpenStreetMap Nominatim (free, no API key needed).
 */
async function reverseGeocode(coords: GPSCoordinates): Promise<string | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${coords.latitude}&lon=${coords.longitude}&format=json&zoom=18`,
      {
        headers: {
          'Accept-Language': 'pt-BR',
        },
      }
    )
    const data = await response.json()
    if (data.display_name) {
      // Simplify address (remove country, postcode, etc.)
      const parts = data.display_name.split(', ')
      return parts.slice(0, 4).join(', ')
    }
  } catch {
    // Ignore geocoding errors
  }
  return null
}
