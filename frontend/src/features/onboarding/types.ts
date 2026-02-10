export type StepStatus = 'pending' | 'completed' | 'skipped'

export const STEP_KEYS = ['branding', 'template', 'first_report'] as const
export type StepKey = typeof STEP_KEYS[number]

export interface OnboardingStep {
  key: StepKey
  status: StepStatus
  label: string
}

export interface OnboardingStatus {
  id: string
  tenant_id: string
  is_completed: boolean
  completed_at: string | null
  current_step: number
  steps: OnboardingStep[]
  metadata_json: Record<string, unknown>
}

export interface StepUpdateRequest {
  action: 'complete' | 'skip'
}

export interface StepUpdateResponse {
  step_key: string
  new_status: string
  is_completed: boolean
  current_step: number
}

export interface CloneDemoTemplateResponse {
  template_id: string
  template_name: string
  template_code: string
}
