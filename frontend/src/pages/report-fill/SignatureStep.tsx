import {
  SignatureSection,
  type SignatureData,
  type SignatureField,
} from '@/features/signature'

interface SignatureStepProps {
  signatures: SignatureData[]
  signatureFields: SignatureField[]
  onAddSignature: (roleName: string, blob: Blob, signerName?: string, fieldId?: string) => Promise<void>
  onDeleteSignature: (signatureId: string) => Promise<void>
  isReadOnly: boolean
}

export function SignatureStep({
  signatures,
  signatureFields,
  onAddSignature,
  onDeleteSignature,
  isReadOnly,
}: SignatureStepProps) {
  if (!signatureFields || signatureFields.length === 0) return null

  return (
    <SignatureSection
      signatures={signatures}
      signatureFields={signatureFields}
      onAddSignature={onAddSignature}
      onDeleteSignature={onDeleteSignature}
      isReadOnly={isReadOnly}
    />
  )
}
