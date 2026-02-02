import { useState } from 'react'
import { Camera, X, Trash2, Image as ImageIcon, ChevronLeft, ChevronRight, MapPin, Clock } from 'lucide-react'
import type { PhotoMetadata } from '../api/photoApi'

interface PhotoGalleryProps {
  photos: PhotoMetadata[]
  maxPhotos?: number
  required?: boolean
  onAddPhoto: () => void
  onDeletePhoto: (photoId: string) => void
  isReadOnly?: boolean
}

export function PhotoGallery({
  photos,
  maxPhotos,
  required,
  onAddPhoto,
  onDeletePhoto,
  isReadOnly = false,
}: PhotoGalleryProps) {
  const [viewerOpen, setViewerOpen] = useState(false)
  const [viewerIndex, setViewerIndex] = useState(0)

  const canAddMore = !maxPhotos || photos.length < maxPhotos
  const needsPhotos = required && photos.length === 0

  const openViewer = (index: number) => {
    setViewerIndex(index)
    setViewerOpen(true)
  }

  return (
    <div className="space-y-2">
      {/* Thumbnails Grid */}
      <div className="flex flex-wrap gap-2">
        {photos.map((photo, index) => (
          <div
            key={photo.id}
            className="relative group w-16 h-16 rounded-lg overflow-hidden border border-gray-200 cursor-pointer"
            onClick={() => openViewer(index)}
          >
            <img
              src={photo.thumbnail_url || photo.url}
              alt={`Foto ${index + 1}`}
              className="w-full h-full object-cover"
            />
            {!isReadOnly && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDeletePhoto(photo.id)
                }}
                className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </div>
        ))}

        {/* Add Photo Button */}
        {!isReadOnly && canAddMore && (
          <button
            onClick={onAddPhoto}
            className={`w-16 h-16 rounded-lg border-2 border-dashed flex items-center justify-center transition-colors ${
              needsPhotos
                ? 'border-red-300 bg-red-50 text-red-500 hover:bg-red-100'
                : 'border-gray-300 bg-gray-50 text-gray-400 hover:bg-gray-100 hover:text-gray-600'
            }`}
          >
            <Camera className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Photo count / required indicator */}
      {(maxPhotos || required) && (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <ImageIcon className="h-3 w-3" />
          <span>
            {photos.length}
            {maxPhotos ? `/${maxPhotos}` : ''} foto(s)
            {required && photos.length === 0 && (
              <span className="text-red-500 ml-1">(obrigatorio)</span>
            )}
          </span>
        </div>
      )}

      {/* Photo Viewer Modal */}
      {viewerOpen && (
        <PhotoViewer
          photos={photos}
          currentIndex={viewerIndex}
          onClose={() => setViewerOpen(false)}
          onNavigate={setViewerIndex}
          onDelete={isReadOnly ? undefined : onDeletePhoto}
        />
      )}
    </div>
  )
}

interface PhotoViewerProps {
  photos: PhotoMetadata[]
  currentIndex: number
  onClose: () => void
  onNavigate: (index: number) => void
  onDelete?: (photoId: string) => void
}

function PhotoViewer({
  photos,
  currentIndex,
  onClose,
  onNavigate,
  onDelete,
}: PhotoViewerProps) {
  const photo = photos[currentIndex]
  const hasPrev = currentIndex > 0
  const hasNext = currentIndex < photos.length - 1

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const handleDelete = () => {
    if (onDelete) {
      onDelete(photo.id)
      if (photos.length === 1) {
        onClose()
      } else if (currentIndex >= photos.length - 1) {
        onNavigate(currentIndex - 1)
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 text-white">
        <button onClick={onClose} className="p-2">
          <X className="h-6 w-6" />
        </button>
        <span className="text-sm">
          {currentIndex + 1} / {photos.length}
        </span>
        {onDelete && (
          <button onClick={handleDelete} className="p-2 text-red-400">
            <Trash2 className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Image */}
      <div className="flex-1 relative flex items-center justify-center">
        <img
          src={photo.url}
          alt={`Foto ${currentIndex + 1}`}
          className="max-w-full max-h-full object-contain"
        />

        {/* Navigation Arrows */}
        {hasPrev && (
          <button
            onClick={() => onNavigate(currentIndex - 1)}
            className="absolute left-4 p-2 bg-black/50 rounded-full text-white"
          >
            <ChevronLeft className="h-8 w-8" />
          </button>
        )}
        {hasNext && (
          <button
            onClick={() => onNavigate(currentIndex + 1)}
            className="absolute right-4 p-2 bg-black/50 rounded-full text-white"
          >
            <ChevronRight className="h-8 w-8" />
          </button>
        )}
      </div>

      {/* Metadata Footer */}
      <div className="bg-black/80 text-white p-4 space-y-1">
        <div className="flex items-center gap-2 text-sm">
          <Clock className="h-4 w-4" />
          {formatDate(photo.captured_at)}
        </div>
        {photo.address && (
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-4 w-4" />
            {photo.address}
          </div>
        )}
        {photo.gps && (
          <div className="text-xs text-gray-400">
            GPS: {photo.gps.latitude.toFixed(6)}, {photo.gps.longitude.toFixed(6)}
            {photo.gps.accuracy && ` (±${photo.gps.accuracy.toFixed(0)}m)`}
          </div>
        )}
      </div>
    </div>
  )
}
