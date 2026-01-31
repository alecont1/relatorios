export interface Tenant {
  id: string
  name: string
  slug: string
  is_active: boolean
  logo_primary_key: string | null
  logo_secondary_key: string | null
  brand_color_primary: string | null
  brand_color_secondary: string | null
  brand_color_accent: string | null
  contact_address: string | null
  contact_phone: string | null
  contact_email: string | null
  contact_website: string | null
  created_at: string
  updated_at: string
}

export interface TenantsListResponse {
  tenants: Tenant[]
  total: number
}

export interface CreateTenantRequest {
  name: string
  slug: string
}

export interface UpdateTenantRequest {
  name?: string
  is_active?: boolean
}

export interface UpdateBrandingRequest {
  brand_color_primary?: string | null
  brand_color_secondary?: string | null
  brand_color_accent?: string | null
  contact_address?: string | null
  contact_phone?: string | null
  contact_email?: string | null
  contact_website?: string | null
}

export interface LogoUploadUrlRequest {
  logo_type: 'primary' | 'secondary'
  filename: string
}

export interface LogoUploadUrlResponse {
  upload_url: string
  object_key: string
}

export interface LogoConfirmRequest {
  logo_type: 'primary' | 'secondary'
  object_key: string
}
