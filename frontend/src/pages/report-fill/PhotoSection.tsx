import {
  CameraCapture,
  type CaptureMetadata,
} from '@/features/photo'

interface PhotoSectionProps {
  cameraOpen: boolean
  onCameraClose: () => void
  onCapture: (blob: Blob, metadata: CaptureMetadata) => Promise<void>
  tenantLogo: string | undefined
  projectName: string | undefined
  watermarkText: string | undefined
}

export function PhotoSection({
  cameraOpen,
  onCameraClose,
  onCapture,
  tenantLogo,
  projectName,
  watermarkText,
}: PhotoSectionProps) {
  return (
    <CameraCapture
      isOpen={cameraOpen}
      onClose={onCameraClose}
      onCapture={onCapture}
      tenantLogo={tenantLogo}
      projectName={projectName}
      watermarkText={watermarkText}
      requireGPS={false}
    />
  )
}
