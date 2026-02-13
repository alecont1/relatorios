import { Cloud, CloudOff, Loader2 } from 'lucide-react'

interface AutoSaveStatusProps {
  status: 'idle' | 'pending' | 'saving' | 'saved' | 'error'
  lastSaved: Date | null
  error: string | null
}

export function AutoSaveStatus({ status, lastSaved, error }: AutoSaveStatusProps) {
  const formatTime = (date: Date) => date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  switch (status) {
    case 'pending':
      return (
        <span className="flex items-center gap-1.5 text-sm text-gray-400">
          <Cloud className="h-4 w-4" />
          Alteracoes pendentes...
        </span>
      )
    case 'saving':
      return (
        <span className="flex items-center gap-1.5 text-sm text-blue-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Salvando...
        </span>
      )
    case 'saved':
      return (
        <span className="flex items-center gap-1.5 text-sm text-green-600">
          <Cloud className="h-4 w-4" />
          Salvo {lastSaved && `as ${formatTime(lastSaved)}`}
        </span>
      )
    case 'error':
      return (
        <span className="flex items-center gap-1.5 text-sm text-red-500" title={error || undefined}>
          <CloudOff className="h-4 w-4" />
          Erro ao salvar
        </span>
      )
    default:
      return null
  }
}
