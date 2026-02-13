import {
  CertificateSelectionModal,
  type Certificate,
} from '@/features/report/components/CertificateSelectionModal'

interface CertificateSelectorProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (certificates: Certificate[]) => void
  reportId: string
  isLoading: boolean
}

export function CertificateSelector({
  isOpen,
  onClose,
  onConfirm,
  reportId,
  isLoading,
}: CertificateSelectorProps) {
  return (
    <CertificateSelectionModal
      isOpen={isOpen}
      onClose={onClose}
      onConfirm={onConfirm}
      reportId={reportId}
      isLoading={isLoading}
    />
  )
}
