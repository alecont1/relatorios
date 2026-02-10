// API hooks
export { useOnboardingStatus, useUpdateStep, useCloneDemoTemplate } from './api'

// Hooks
export { useOnboardingGuard } from './hooks/useOnboardingGuard'
export { useOnboardingTour } from './hooks/useOnboardingTour'

// Components
export {
  OnboardingProgress,
  BrandingStep,
  TemplateStep,
  CertificateStep,
  UsersStep,
  FirstReportStep,
  OnboardingBanner,
} from './components'

// Types
export type {
  StepStatus,
  StepKey,
  OnboardingStep,
  OnboardingStatus,
  StepUpdateRequest,
  StepUpdateResponse,
  CloneDemoTemplateResponse,
} from './types'
export { STEP_KEYS } from './types'
