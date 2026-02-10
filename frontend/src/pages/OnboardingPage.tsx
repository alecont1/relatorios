import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Joyride from 'react-joyride'
import { ArrowLeft, ArrowRight, SkipForward, Loader2 } from 'lucide-react'
import {
  useOnboardingStatus,
  useUpdateStep,
  OnboardingProgress,
  BrandingStep,
  TemplateStep,
  CertificateStep,
  FirstReportStep,
  STEP_KEYS,
} from '@/features/onboarding'
import { useOnboardingTour } from '@/features/onboarding/hooks/useOnboardingTour'
import type { StepKey } from '@/features/onboarding'

export function OnboardingPage() {
  const navigate = useNavigate()
  const { data: status, isLoading } = useOnboardingStatus()
  const updateStep = useUpdateStep()
  const [activeStep, setActiveStep] = useState(0)
  const [tourStarted, setTourStarted] = useState<Set<number>>(new Set())

  const currentStepKey = STEP_KEYS[activeStep] as StepKey
  const { run, steps: tourSteps, startTour, handleJoyrideCallback } = useOnboardingTour(currentStepKey)

  // Recovery: set activeStep from server state on load
  useEffect(() => {
    if (status) {
      if (status.is_completed) {
        navigate('/', { replace: true })
        return
      }
      setActiveStep(status.current_step < STEP_KEYS.length ? status.current_step : 0)
    }
  }, [status, navigate])

  // Auto-start tour on first visit to each step
  useEffect(() => {
    if (!tourStarted.has(activeStep) && tourSteps.length > 0) {
      const timer = setTimeout(() => {
        startTour()
        setTourStarted((prev) => new Set(prev).add(activeStep))
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [activeStep, tourStarted, tourSteps.length, startTour])

  const handleStepComplete = useCallback(async () => {
    const stepKey = STEP_KEYS[activeStep]
    const result = await updateStep.mutateAsync({ key: stepKey, action: 'complete' })

    if (result.is_completed) {
      navigate('/', { replace: true })
    } else if (activeStep < STEP_KEYS.length - 1) {
      setActiveStep((prev) => prev + 1)
    }
  }, [activeStep, updateStep, navigate])

  const handleSkip = async () => {
    const stepKey = STEP_KEYS[activeStep]
    const result = await updateStep.mutateAsync({ key: stepKey, action: 'skip' })

    if (result.is_completed) {
      navigate('/', { replace: true })
    } else if (activeStep < STEP_KEYS.length - 1) {
      setActiveStep((prev) => prev + 1)
    }
  }

  const handleBack = () => {
    if (activeStep > 0) {
      setActiveStep((prev) => prev - 1)
    }
  }

  if (isLoading || !status) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Joyride
        run={run}
        steps={tourSteps}
        callback={handleJoyrideCallback}
        continuous
        showSkipButton
        showProgress
        styles={{
          options: {
            primaryColor: '#2563eb',
            zIndex: 10000,
          },
        }}
        locale={{
          back: 'Voltar',
          close: 'Fechar',
          last: 'Finalizar',
          next: 'Proximo',
          skip: 'Pular tour',
        }}
      />

      {/* Header */}
      <div className="border-b bg-white">
        <div className="mx-auto max-w-4xl px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Configuracao Inicial
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Siga os passos abaixo para configurar sua empresa no SmartHand
          </p>

          {/* Progress */}
          <div className="mt-6">
            <OnboardingProgress steps={status.steps} activeStep={activeStep} />
          </div>
        </div>
      </div>

      {/* Step content */}
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          {activeStep === 0 && <BrandingStep onComplete={handleStepComplete} />}
          {activeStep === 1 && <TemplateStep onComplete={handleStepComplete} />}
          {activeStep === 2 && <CertificateStep onComplete={handleStepComplete} />}
          {activeStep === 3 && <FirstReportStep onComplete={handleStepComplete} />}
        </div>

        {/* Navigation */}
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={activeStep === 0}
            className="flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar
          </button>

          <div className="flex gap-3">
            <button
              onClick={handleSkip}
              disabled={updateStep.isPending}
              className="flex items-center gap-2 rounded-lg border border-orange-300 px-4 py-2 text-orange-700 hover:bg-orange-50 disabled:opacity-50"
            >
              <SkipForward className="h-4 w-4" />
              Pular passo
            </button>

            {activeStep < STEP_KEYS.length - 1 && (
              <button
                onClick={() => setActiveStep((prev) => prev + 1)}
                className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-2 text-gray-700 hover:bg-gray-200"
              >
                Proximo
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
