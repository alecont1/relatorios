import { create } from 'zustand'

interface AppState {
  isOnline: boolean
  currentTenant: string | null
  setOnline: (online: boolean) => void
  setTenant: (tenantId: string | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  isOnline: navigator.onLine,
  currentTenant: null,
  setOnline: (online) => set({ isOnline: online }),
  setTenant: (tenantId) => set({ currentTenant: tenantId }),
}))
