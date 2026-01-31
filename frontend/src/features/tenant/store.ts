import { create } from 'zustand'
import type { Tenant } from './types'

interface TenantState {
  branding: Tenant | null
  isLoading: boolean
  setBranding: (branding: Tenant) => void
  clearBranding: () => void
}

export const useTenantStore = create<TenantState>((set) => ({
  branding: null,
  isLoading: false,
  setBranding: (branding) => set({ branding, isLoading: false }),
  clearBranding: () => set({ branding: null }),
}))
