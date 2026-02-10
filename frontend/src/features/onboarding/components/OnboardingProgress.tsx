import { Check } from 'lucide-react'
import type { OnboardingStep, StepKey } from '../types'

const STEP_LABELS: Record<StepKey, string> = {
  branding: 'Identidade Visual',
  template: 'Template',
  certificate: 'Certificados',
  first_report: 'Primeiro Relatorio',
}

interface OnboardingProgressProps {
  steps: OnboardingStep[]
  activeStep: number
}

export function OnboardingProgress({ steps, activeStep }: OnboardingProgressProps) {
  return (
    <div className="flex items-center justify-center gap-2">
      {steps.map((step, i) => {
        const isCompleted = step.status === 'completed'
        const isSkipped = step.status === 'skipped'
        const isActive = i === activeStep
        const isPending = step.status === 'pending' && !isActive

        return (
          <div key={step.key} className="flex items-center gap-2">
            {/* Step circle */}
            <div className="flex flex-col items-center gap-1">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-medium transition-colors ${
                  isCompleted
                    ? 'bg-green-100 text-green-700'
                    : isSkipped
                    ? 'bg-orange-100 text-orange-700'
                    : isActive
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-400'
                }`}
              >
                {isCompleted ? (
                  <Check className="h-5 w-5" />
                ) : isSkipped ? (
                  <span className="text-xs">Pular</span>
                ) : (
                  i + 1
                )}
              </div>
              <span
                className={`text-xs whitespace-nowrap ${
                  isActive ? 'font-semibold text-blue-700' : isCompleted ? 'text-green-700' : isSkipped ? 'text-orange-600' : 'text-gray-400'
                }`}
              >
                {STEP_LABELS[step.key]}
              </span>
            </div>

            {/* Connector line */}
            {i < steps.length - 1 && (
              <div
                className={`h-0.5 w-8 ${
                  isCompleted || isSkipped ? 'bg-green-300' : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
