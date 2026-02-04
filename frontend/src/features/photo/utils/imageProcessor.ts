/**
 * Image processing utilities for compression and watermarking.
 */

interface CompressOptions {
  maxWidth?: number
  maxHeight?: number
  quality?: number
}

interface WatermarkOptions {
  timestamp: Date
  address?: string
  tenantLogo?: string
}

/**
 * Compress an image blob.
 */
export async function compressImage(
  blob: Blob,
  options: CompressOptions = {}
): Promise<Blob> {
  const { maxWidth = 1920, maxHeight = 1080, quality = 0.85 } = options

  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      // Calculate new dimensions
      let width = img.width
      let height = img.height

      if (width > maxWidth) {
        height = (height * maxWidth) / width
        width = maxWidth
      }
      if (height > maxHeight) {
        width = (width * maxHeight) / height
        height = maxHeight
      }

      // Create canvas and draw resized image
      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('Failed to get canvas context'))
        return
      }

      ctx.drawImage(img, 0, 0, width, height)

      // Convert to blob
      canvas.toBlob(
        (result) => {
          if (result) {
            resolve(result)
          } else {
            reject(new Error('Failed to compress image'))
          }
        },
        'image/jpeg',
        quality
      )
    }

    img.onerror = () => reject(new Error('Failed to load image'))
    img.src = URL.createObjectURL(blob)
  })
}

/**
 * Add watermark to an image.
 */
export async function addWatermark(
  blob: Blob,
  options: WatermarkOptions
): Promise<Blob> {
  const { timestamp, address, tenantLogo } = options

  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = async () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('Failed to get canvas context'))
        return
      }

      // Draw original image
      ctx.drawImage(img, 0, 0)

      // Calculate watermark area height (10% of image height, min 60px)
      const watermarkHeight = Math.max(img.height * 0.1, 60)
      const padding = watermarkHeight * 0.15
      const fontSize = Math.max(watermarkHeight * 0.3, 14)

      // Draw semi-transparent bottom strip
      ctx.fillStyle = 'rgba(0, 0, 0, 0.6)'
      ctx.fillRect(0, img.height - watermarkHeight, img.width, watermarkHeight)

      // Draw tenant logo if provided
      if (tenantLogo) {
        try {
          const logo = await loadImage(tenantLogo)
          const logoHeight = watermarkHeight - padding * 2
          const logoWidth = (logo.width / logo.height) * logoHeight
          ctx.drawImage(logo, padding, img.height - watermarkHeight + padding, logoWidth, logoHeight)
        } catch {
          // Ignore logo loading errors
        }
      }

      // Draw watermark text
      ctx.fillStyle = '#ffffff'
      ctx.textBaseline = 'top'

      const textY = img.height - watermarkHeight + padding
      const lineHeight = fontSize + padding * 0.3

      // Draw date/time (first line - more prominent)
      ctx.font = `bold ${fontSize}px Arial, sans-serif`
      ctx.textAlign = 'right'
      const dateStr = formatDateTime(timestamp)
      ctx.fillText(`📅 ${dateStr}`, img.width - padding, textY)

      // Draw address if provided (second line)
      if (address) {
        ctx.font = `${fontSize * 0.85}px Arial, sans-serif`
        ctx.textAlign = 'right'
        ctx.fillText(
          `📍 ${truncateText(address, 45)}`,
          img.width - padding,
          textY + lineHeight
        )
      }

      // Convert to blob
      canvas.toBlob(
        (result) => {
          if (result) {
            resolve(result)
          } else {
            reject(new Error('Failed to add watermark'))
          }
        },
        'image/jpeg',
        0.92
      )
    }

    img.onerror = () => reject(new Error('Failed to load image'))
    img.src = URL.createObjectURL(blob)
  })
}

/**
 * Generate a thumbnail from an image blob.
 */
export async function generateThumbnail(
  blob: Blob,
  size: number = 200
): Promise<Blob> {
  return compressImage(blob, {
    maxWidth: size,
    maxHeight: size,
    quality: 0.8,
  })
}

/**
 * Process image: compress and optionally add watermark.
 */
export async function processImage(
  blob: Blob,
  watermarkOptions?: WatermarkOptions
): Promise<Blob> {
  // First compress
  let processed = await compressImage(blob)

  // Then add watermark if options provided
  if (watermarkOptions) {
    processed = await addWatermark(processed, watermarkOptions)
  }

  return processed
}

// Helper functions
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('Failed to load image'))
    img.src = src
  })
}

function formatDateTime(date: Date): string {
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + '...'
}
