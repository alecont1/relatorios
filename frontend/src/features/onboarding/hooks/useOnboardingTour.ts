import { useState, useCallback } from 'react'
import type { Step, CallBackProps, STATUS_EVENTS } from 'react-joyride'
import type { StepKey } from '../types'

const TOUR_STEPS: Record<StepKey, Step[]> = {
  branding: [
    {
      target: '.onboarding-branding-logos',
      content: 'Faca upload dos logos da sua empresa. Eles aparecerão nos relatorios gerados.',
      disableBeacon: true,
    },
    {
      target: '.onboarding-branding-colors',
      content: 'Escolha as cores da marca para personalizar a interface e os relatorios.',
    },
    {
      target: '.onboarding-branding-contact',
      content: 'Preencha as informacoes de contato que aparecerão nos relatorios.',
    },
  ],
  template: [
    {
      target: '.onboarding-template-clone',
      content: 'Clique aqui para clonar o template demo CPQ11. Voce podera personaliza-lo depois.',
      disableBeacon: true,
    },
  ],
  certificate: [
    {
      target: '.onboarding-certificate-form',
      content: 'Cadastre os certificados de calibracao dos seus equipamentos de medicao.',
      disableBeacon: true,
    },
  ],
  first_report: [
    {
      target: '.onboarding-report-form',
      content: 'Crie seu primeiro relatorio usando o template demo. Isso ajuda a entender o fluxo completo.',
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
