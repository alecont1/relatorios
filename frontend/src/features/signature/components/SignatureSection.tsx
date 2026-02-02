import { useState } from 'react'
import { PenLine, Trash2, Check, AlertCircle } from 'lucide-react'
import { SignaturePad } from './SignaturePad'
import type { SignatureData, SignatureField } from '../api/signatureApi'

interface SignatureSectionProps {
  signatures: SignatureData[]
  signatureFields: SignatureField[]
  onAddSignature: (
    roleNname: string,
    blob: Blob,
    signerName?: string,
    fieldId?: string
  ) => Promise<void>
  onDeleteSignature: (signatureId: string) => Promise<void>
  isReadOnly: boolean
}

export function SignatureSection({
  signatures,
  signatureFields,
  onAddSignature,
  onDeleteSignature,
  isReadOnly,
}: SignatureSectionProps) {
  const [showPad, setShowPad] = useState(false)
  const [activeRole, setActiveRole] = useState<string>('')
  const [activeFieldId, setActiveFieldId] = useState<string | undefined>()
  const [signerName, setSignerName] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Get signature for a role
  const getSignatureForRole = (roleName: string): SignatureData | undefined => {
    return signatures.find((s) => s.role_name === roleName)
  }

  // Handle opening signature pad
  const handleOpenPad = (roleName: string, fieldId?: string) => {
    setActiveRole(roleName)
    setActiveFieldId(fieldId)
    setSignerName('')
    setShowPad(true)
  }

  // Handle saving signature
  const handleSaveSignature = async (blob: Blob) => {
    setIsLoading(true)
    try {
      await onAddSignature(activeRole, blob, signerName, activeFieldId)
      setShowPad(false)
    } catch (error) {
      console.error('Failed to save signature:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Handle deleting signature
  const handleDelete = async (signatureId: string) => {
    if (!confirm('Deseja realmente excluir esta assinatura?')) return

    setIsLoading(true)
    try {
      await onDeleteSignature(signatureId)
    } catch (error) {
      console.error('Failed to delete signature:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Check if all required signatures are present
  const requiredFields = signatureFields.filter((f) => f.required)
  const missingRequired = requiredFields.filter(
    (f) => !getSignatureForRole(f.role_name)
  )

  return (
    <div className="bg-white border rounded-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <PenLine className="h-5 w-5 text-blue-600" />
            <h3 className="font-medium text-gray-900">Assinaturas</h3>
          </div>
          {missingRequired.length > 0 && !isReadOnly && (
            <span className="flex items-center gap-1 text-sm text-amber-600">
              <AlertCircle className="h-4 w-4" />
              {missingRequired.length} obrigatoria(s) pendente(s)
            </span>
          )}
        </div>
      </div>

      {/* Signature fields */}
      <div className="divide-y">
        {signatureFields.map((field) => {
          const signature = getSignatureForRole(field.role_name)
          const isSigned = !!signature

          return (
            <div key={field.id} className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      {field.role_name}
                    </span>
                    {field.required && (
                      <span className="text-xs text-red-500">*obrigatoria</span>
                    )}
                    {isSigned && (
                      <span className="flex items-center gap-1 text-xs text-green-600">
                        <Check className="h-3 w-3" />
                        Assinado
                      </span>
                    )}
                  </div>

                  {signature && (
                    <div className="mt-2">
                      {/* Signature preview */}
                      <div className="relative inline-block">
                        <img
                          src={signature.url}
                          alt={`Assinatura de ${field.role_name}`}
                          className="h-20 border border-gray-200 rounded bg-white"
                        />
                        {!isReadOnly && (
                          <button
                            onClick={() => handleDelete(signature.id)}
                            disabled={isLoading}
                            className="absolute -top-2 -right-2 p-1 bg-red-100 text-red-600 rounded-full hover:bg-red-200 disabled:opacity-50"
                            title="Excluir assinatura"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        )}
                      </div>

                      {/* Signature details */}
                      <div className="mt-1 text-xs text-gray-500">
                        {signature.signer_name && (
                          <p>{signature.signer_name}</p>
                        )}
                        <p>
                          {new Date(signature.signed_at).toLocaleString('pt-BR', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Sign button */}
                {!isReadOnly && !isSigned && (
                  <button
                    onClick={() => handleOpenPad(field.role_name, field.id)}
                    disabled={isLoading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    <PenLine className="h-4 w-4" />
                    Assinar
                  </button>
                )}
              </div>
            </div>
          )
        })}

        {/* Empty state */}
        {signatureFields.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            <PenLine className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            <p>Nenhum campo de assinatura configurado</p>
          </div>
        )}
      </div>

      {/* Signature Pad Modal */}
      <SignaturePad
        isOpen={showPad}
        onClose={() => setShowPad(false)}
        onSave={handleSaveSignature}
        roleName={activeRole}
        signerName={signerName}
        onSignerNameChange={setSignerName}
      />
    </div>
  )
}
