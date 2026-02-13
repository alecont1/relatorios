import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { GitBranch, Loader2, X } from 'lucide-react'
import { reportApi } from '../api/reportApi'

interface RevisionButtonProps {
  reportId: string
  reportStatus: string
}

export function RevisionButton({ reportId, reportStatus }: RevisionButtonProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDialog, setShowDialog] = useState(false)
  const [notes, setNotes] = useState('')

  const mutation = useMutation({
    mutationFn: () => reportApi.createRevision(reportId, notes || undefined),
    onSuccess: (newReport) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setShowDialog(false)
      setNotes('')
      navigate(`/reports/${newReport.id}`)
    },
  })

  if (reportStatus !== 'completed') {
    return null
  }

  return (
    <>
      <button
        onClick={() => setShowDialog(true)}
        className="flex items-center gap-2 px-4 py-2 text-amber-700 bg-amber-50 rounded-lg hover:bg-amber-100 border border-amber-200"
      >
        <GitBranch className="h-4 w-4" />
        Criar Revisao
      </button>

      {showDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                Criar Revisao
              </h3>
              <button
                onClick={() => setShowDialog(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <p className="text-sm text-gray-600">
                Uma nova revisao sera criada como rascunho, copiando todos os
                dados do relatorio atual. Voce podera editar e concluir a nova
                versao.
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas da revisao (opcional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Descreva o motivo da revisao..."
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                />
              </div>

              {mutation.isError && (
                <p className="text-sm text-red-600">
                  Erro ao criar revisao. Tente novamente.
                </p>
              )}
            </div>

            <div className="flex justify-end gap-3 p-4 border-t">
              <button
                onClick={() => setShowDialog(false)}
                disabled={mutation.isPending}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancelar
              </button>
              <button
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
              >
                {mutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <GitBranch className="h-4 w-4" />
                )}
                {mutation.isPending ? 'Criando...' : 'Criar Revisao'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
