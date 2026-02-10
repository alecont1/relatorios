import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './store'
import type { User } from './types'

const mockUser: User = {
  id: 'user-1',
  email: 'tecnico@smarthand.com',
  full_name: 'Joao Silva',
  role: 'technician',
  tenant_id: 'tenant-abc',
  is_active: true,
  created_at: '2025-01-15T10:00:00Z',
}

describe('useAuthStore', () => {
  beforeEach(() => {
    // Reset the store state before each test
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
    })
    localStorage.clear()
  })

  it('setAuth stores user and access token', () => {
    const { setAuth } = useAuthStore.getState()

    setAuth(mockUser, 'jwt-token-123')

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockUser)
    expect(state.accessToken).toBe('jwt-token-123')
  })

  it('clearAuth removes user and access token', () => {
    const { setAuth, clearAuth } = useAuthStore.getState()

    setAuth(mockUser, 'jwt-token-123')
    clearAuth()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
  })

  it('isAuthenticated is true after setAuth', () => {
    const { setAuth } = useAuthStore.getState()

    setAuth(mockUser, 'jwt-token-123')

    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })

  it('isAuthenticated is false after clearAuth', () => {
    const { setAuth, clearAuth } = useAuthStore.getState()

    setAuth(mockUser, 'jwt-token-123')
    expect(useAuthStore.getState().isAuthenticated).toBe(true)

    clearAuth()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })

  it('persists user info to localStorage but not the access token', () => {
    const { setAuth } = useAuthStore.getState()

    setAuth(mockUser, 'jwt-token-secret')

    // The persist middleware stores under the key "smarthand-auth"
    const stored = JSON.parse(localStorage.getItem('smarthand-auth') || '{}')

    // user is persisted
    expect(stored.state?.user).toEqual(mockUser)
    // isAuthenticated is persisted
    expect(stored.state?.isAuthenticated).toBe(true)
    // accessToken must NOT be persisted (security - partialize excludes it)
    expect(stored.state?.accessToken).toBeUndefined()
  })

  it('setLoading updates isLoading state', () => {
    const { setLoading } = useAuthStore.getState()

    setLoading(false)
    expect(useAuthStore.getState().isLoading).toBe(false)

    setLoading(true)
    expect(useAuthStore.getState().isLoading).toBe(true)
  })

  it('setAccessToken updates only the token', () => {
    const { setAuth, setAccessToken } = useAuthStore.getState()

    setAuth(mockUser, 'old-token')
    setAccessToken('new-token')

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('new-token')
    expect(state.user).toEqual(mockUser)
    expect(state.isAuthenticated).toBe(true)
  })
})
