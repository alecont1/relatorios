import { useState } from 'react'
import { HexColorPicker } from 'react-colorful'

interface Props {
  label: string
  value: string | null
  onChange: (color: string) => void
}

export function ColorPicker({ label, value, onChange }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const currentColor = value || '#3B82F6'

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="mt-1 flex items-center gap-3">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="h-10 w-10 rounded border-2 border-gray-300 shadow-sm"
          style={{ backgroundColor: currentColor }}
          aria-label={`Selecionar ${label.toLowerCase()}`}
        />
        <span className="text-sm text-gray-600 font-mono">{currentColor}</span>
      </div>

      {isOpen && (
        <div className="mt-2">
          <HexColorPicker color={currentColor} onChange={onChange} />
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="mt-2 text-sm text-gray-500 hover:text-gray-700"
          >
            Fechar
          </button>
        </div>
      )}
    </div>
  )
}
