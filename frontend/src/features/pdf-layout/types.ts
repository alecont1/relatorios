export interface PdfLayout {
  id: string
  tenant_id: string | null
  name: string
  slug: string
  description: string | null
  config_json: PdfLayoutConfig
  is_system: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PdfLayoutConfig {
  cover_page?: { enabled: boolean }
  fonts?: { base_size: number; header_size: number; section_size: number }
  margins?: { top: number; right: number; bottom: number; left: number }
  photos?: { columns: number; max_per_section: number; width_mm: number; height_mm: number }
  checklist?: { show_all_items: boolean; highlight_non_conforming: boolean }
  certificates?: { show_table: boolean }
  signatures?: { columns: number; box_width_mm: number; box_height_mm: number }
}

export interface PdfLayoutListResponse {
  layouts: PdfLayout[]
  total: number
}
