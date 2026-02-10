// Limits and Features

export interface TenantLimits {
  max_users: number
  max_storage_gb: number
  max_reports_month: number
}

export interface TenantFeatures {
  gps_required: boolean
  certificate_required: boolean
  export_excel: boolean
  watermark: boolean
  custom_pdf: boolean
}

// Plans

export interface TenantPlan {
  id: string
  name: string
  description: string | null
  limits: TenantLimits
  features: TenantFeatures
  is_active: boolean
  price_display: string | null
  created_at: string
}

// Config

export type TenantStatus = 'trial' | 'active' | 'suspended'

export interface TenantConfig {
  id: string
  tenant_id: string
  status: TenantStatus
  contract_type: string | null
  limits: TenantLimits
  features: TenantFeatures
  suspended_at: string | null
  suspended_reason: string | null
  trial_ends_at: string | null
  plan_id: string | null
  plan: TenantPlan | null
}

// Usage stats

export interface TenantUsage {
  users_count: number
  storage_used_gb: number
  reports_this_month: number
}

// Combined tenant with config for list views

export interface TenantWithConfig {
  id: string
  name: string
  slug: string
  is_active: boolean
  logo_primary_key: string | null
  logo_secondary_key: string | null
  brand_color_primary: string | null
  created_at: string
  config: TenantConfig
  usage?: TenantUsage
}

// Request types

export interface CreateTenantWithConfig {
  name: string
  slug: string
  plan_id: string
  admin_email: string
  admin_password: string
  admin_full_name: string
  contract_type?: string
  trial_days?: number
  brand_color_primary?: string
}

export interface UpdateTenantConfig {
  limits?: Partial<TenantLimits>
  features?: Partial<TenantFeatures>
  contract_type?: string
}

export interface SuspendTenantRequest {
  reason: string
}

export interface AssignPlanRequest {
  plan_id: string
}

export interface CreatePlanRequest {
  name: string
  description?: string
  limits: TenantLimits
  features: TenantFeatures
  price_display?: string
  is_active?: boolean
}

export interface UpdatePlanRequest extends Partial<CreatePlanRequest> {
  id: string
}

// Audit log

export interface TenantAuditLog {
  id: string
  tenant_id: string
  admin_user_id: string
  action: string
  old_values: Record<string, unknown> | null
  new_values: Record<string, unknown> | null
  reason: string | null
  created_at: string
}

// Paginated response

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

// Filter params

export interface TenantFilters {
  status?: TenantStatus
  plan_id?: string
  search?: string
  page?: number
  limit?: number
}
