interface TenantUsageBarProps {
  label: string
  used: number
  max: number
  unit?: string
}

export function TenantUsageBar({ label, used, max, unit }: TenantUsageBarProps) {
  const percentage = max > 0 ? Math.min(100, (used / max) * 100) : 0

  let barColor = 'bg-green-500'
  if (percentage >= 90) {
    barColor = 'bg-red-500'
  } else if (percentage >= 70) {
    barColor = 'bg-yellow-500'
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
        <span>{label}</span>
        <span>
          {used} / {max}{unit ? ` ${unit}` : ''}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
