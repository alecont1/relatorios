import { useEffect } from 'react'
import { useTenantStore } from '../store'

// Default brand colors if tenant hasn't configured any
const DEFAULT_COLORS = {
  primary: '#3B82F6',    // Blue-500
  secondary: '#6366F1',  // Indigo-500
  accent: '#10B981',     // Emerald-500
}

export function useTheme() {
  const { branding } = useTenantStore()

  useEffect(() => {
    const root = document.documentElement

    // Apply brand colors as CSS variables
    root.style.setProperty(
      '--color-brand-primary',
      branding?.brand_color_primary || DEFAULT_COLORS.primary
    )
    root.style.setProperty(
      '--color-brand-secondary',
      branding?.brand_color_secondary || DEFAULT_COLORS.secondary
    )
    root.style.setProperty(
      '--color-brand-accent',
      branding?.brand_color_accent || DEFAULT_COLORS.accent
    )
  }, [branding])
}
