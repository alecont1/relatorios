import { useState, useCallback } from 'react'
import type { Step, CallBackProps, STATUS_EVENTS } from 'react-joyride'
import type { StepKey } from '../types'

const TOUR_STEPS: Record<StepKey, Step[]> = {
  branding: [
    {
      target: '.onboarding-branding-logos',
      content: 'Faca upload dos logos da sua empresa. Veja no preview ao lado como ficara no PDF.',
      disableBeacon: true,
    },
    {
      target: '.onboarding-branding-colors',
      content: 'Escolha as cores da marca. O preview do PDF atualiza em tempo real!',
    },
    {
      target: '.onboarding-branding-contact',
      content: 'Preencha as informacoes de contato que aparecerão no rodape dos relatorios.',
    },
  ],
  template: [
    {
      target: '.onboarding-template-clone',
      content: 'Clone o template demo para ver como seus relatorios serao estruturados.',
      disableBeacon: true,
    },
  ],
  first_report: [
    {
      target: '.onboarding-report-form',
      content: 'Crie seu primeiro relatorio e veja o PDF gerado com sua marca!',
      disableBeacon: true,
    },
  ],
}

export function useOnboardingTour(stepKey: StepKey) {
  const [run, setRun] = useState(false)
  const steps = TOUR_STEPS[stepKey] || []

  const startTour = useCallback(() => {
    setRun(true)
  }, [])

  const handleJoyrideCallback = useCallback((data: CallBackProps) => {
    const { status } = data
    const finishedStatuses: string[] = ['finished', 'skipped']
    if (finishedStatuses.includes(status)) {
      setRun(false)
    }
  }, [])

  return { run, steps, startTour, handleJoyrideCallback }
}
