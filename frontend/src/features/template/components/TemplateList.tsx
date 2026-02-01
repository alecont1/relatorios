import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, ToggleLeft, ToggleRight } from 'lucide-react'
import type { TemplateListItem } from '../api/templateApi'
import { templateApi } from '../api/templateApi'
import { useDebouncedValue } from '../hooks/useDebouncedValue'

interface TemplateListProps {
  onSelectTemplate?: (template: TemplateListItem) => void
}

export function TemplateList({ onSelectTemplate }: TemplateListProps) {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<'active' | 'inactive' | 'all'>('active')
  const debouncedSearch = useDebouncedValue(search, 300)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['templates', debouncedSearch, statusFilter],
    queryFn: () => templateApi.list({ search: debouncedSearch, status: statusFilter }),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      templateApi.update(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
    },
  })

  const getCategoryBadgeColor = (category: string) => {
    const colors: Record<string, string> = {
      Commissioning: 'bg-blue-100 text-blue-800',
      Inspection: 'bg-green-100 text-green-800',
      Maintenance: 'bg-yellow-100 text-yellow-800',
      Testing: 'bg-purple-100 text-purple-800',
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  if (error) {
    return <div className="text-red-600">Erro ao carregar templates</div>
  }

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nome ou codigo..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as 'active' | 'inactive' | 'all')}
          className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
        >
          <option value="active">Ativos</option>
          <option value="inactive">Inativos</option>
          <option value="all">Todos</option>
        </select>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Codigo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Categoria
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Versao
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                Acoes
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  Carregando...
                </td>
              </tr>
            ) : data?.templates.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  Nenhum template encontrado
                </td>
              </tr>
            ) : (
              data?.templates.map((template) => (
                <tr
                  key={template.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => onSelectTemplate?.(template)}
                >
                  <td className="whitespace-nowrap px-6 py-4 font-medium text-gray-900">
                    {template.name}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 font-mono text-sm text-gray-600">
                    {template.code}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${getCategoryBadgeColor(template.category)}`}>
                      {template.category}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-gray-600">
                    v{template.version}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                      template.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {template.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleMutation.mutate({ id: template.id, is_active: !template.is_active })
                      }}
                      className="text-gray-400 hover:text-gray-600"
                      title={template.is_active ? 'Desativar' : 'Ativar'}
                    >
                      {template.is_active ? (
                        <ToggleRight className="h-5 w-5 text-green-600" />
                      ) : (
                        <ToggleLeft className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Total count */}
      {data && (
        <div className="text-sm text-gray-500">
          Total: {data.total} template(s)
        </div>
      )}
    </div>
  )
}
