export interface WatermarkConfig {
  logo: boolean
  gps: boolean
  datetime: boolean
  company_name: boolean
  report_number: boolean
  technician_name: boolean
}

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
  watermark_text: string | null
  watermark_config: WatermarkConfig | null
  default_pdf_layout_id: string | null
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
  watermark_text?: string | null
  watermark_config?: WatermarkConfig | null
  default_pdf_layout_id?: string | null
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

/**
 * Build the public URL for a logo from its R2 object key.
 */
export function getLogoUrl(logoKey: string | null | undefined): string | undefined {
  if (!logoKey) return undefined
  const r2PublicUrl = import.meta.env.VITE_R2_PUBLIC_URL
  if (!r2PublicUrl) return undefined
  return `${r2PublicUrl}/${logoKey}`
}
