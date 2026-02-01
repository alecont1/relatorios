import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import type { ExcelParseResponse } from '../api/templateApi'
import { templateApi } from '../api/templateApi'

interface ExcelUploaderProps {
  onParsed: (result: ExcelParseResponse, file: File) => void
}

export function ExcelUploader({ onParsed }: ExcelUploaderProps) {
  const parseMutation = useMutation({
    mutationFn: templateApi.parse,
  })

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return

      const result = await parseMutation.mutateAsync(file)
      onParsed(result, file)
    },
    [parseMutation, onParsed]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    disabled: parseMutation.isPending,
  })

  return (
    <div
      {...getRootProps()}
      className={`
        rounded-lg border-2 border-dashed p-8 text-center transition-colors cursor-pointer
        ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
        ${parseMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />

      {parseMutation.isPending ? (
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <p className="text-gray-600">Processando arquivo...</p>
        </div>
      ) : parseMutation.isError ? (
        <div className="flex flex-col items-center gap-2 text-red-600">
          <AlertCircle className="h-8 w-8" />
          <p>Erro ao processar arquivo</p>
          <p className="text-sm">Clique para tentar novamente</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          {isDragActive ? (
            <>
              <FileSpreadsheet className="h-8 w-8 text-blue-500" />
              <p className="text-blue-600">Solte o arquivo aqui...</p>
            </>
          ) : (
            <>
              <Upload className="h-8 w-8 text-gray-400" />
              <p className="text-gray-600">
                Arraste um arquivo Excel ou clique para selecionar
              </p>
              <p className="text-sm text-gray-400">
                Formatos aceitos: .xlsx, .xls
              </p>
            </>
          )}
        </div>
      )}
    </div>
  )
}
