import { useEffect, useRef, useCallback, useState } from 'react'

interface AutoSaveOptions<T> {
  data: T
  onSave: (data: T) => Promise<void>
  debounceMs?: number
  enabled?: boolean
  storageKey?: string  // For localStorage draft backup
}

interface AutoSaveState {
  status: 'idle' | 'pending' | 'saving' | 'saved' | 'error'
  lastSaved: Date | null
  error: string | null
}

export function useAutoSave<T>({
  data,
  onSave,
  debounceMs = 2000,
  enabled = true,
  storageKey,
}: AutoSaveOptions<T>) {
  const [state, setState] = useState<AutoSaveState>({
    status: 'idle',
    lastSaved: null,
    error: null,
  })

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const dataRef = useRef<T>(data)
  const isFirstRender = useRef(true)
  const isSaving = useRef(false)

  // Update data ref on change
  useEffect(() => {
    dataRef.current = data
  }, [data])

  // Save to localStorage for draft backup
  useEffect(() => {
    if (storageKey && enabled && !isFirstRender.current) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(data))
      } catch {
        // Ignore storage errors
      }
    }
  }, [data, storageKey, enabled])

  // Clear localStorage backup after successful save
  const clearDraftBackup = useCallback(() => {
    if (storageKey) {
      try {
        localStorage.removeItem(storageKey)
      } catch {
        // Ignore
      }
    }
  }, [storageKey])

  // The actual save function
  const doSave = useCallback(async () => {
    if (isSaving.current) return

    isSaving.current = true
    setState((prev) => ({ ...prev, status: 'saving', error: null }))

    try {
      await onSave(dataRef.current)
      setState({
        status: 'saved',
        lastSaved: new Date(),
        error: null,
      })
      clearDraftBackup()
    } catch (err) {
      setState((prev) => ({
        ...prev,
        status: 'error',
        error: err instanceof Error ? err.message : 'Erro ao salvar',
      }))
    } finally {
      isSaving.current = false
    }
  }, [onSave, clearDraftBackup])

  // Debounced auto-save effect
  useEffect(() => {
    if (!enabled) return

    // Skip first render
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Mark as pending
    setState((prev) => ({ ...prev, status: 'pending' }))

    // Set new timeout for debounced save
    timeoutRef.current = setTimeout(() => {
      doSave()
    }, debounceMs)

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [data, enabled, debounceMs, doSave])

  // Manual save function
  const saveNow = useCallback(async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    await doSave()
  }, [doSave])

  // Load draft backup from localStorage
  const loadDraftBackup = useCallback((): T | null => {
    if (!storageKey) return null
    try {
      const stored = localStorage.getItem(storageKey)
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  }, [storageKey])

  return {
    ...state,
    saveNow,
    loadDraftBackup,
    clearDraftBackup,
    isPending: state.status === 'pending',
    isSaving: state.status === 'saving',
  }
}
