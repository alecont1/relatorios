import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAutoSave } from './useAutoSave'

describe('useAutoSave', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    localStorage.clear()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not save immediately on data change (debounce)', () => {
    const onSave = vi.fn().mockResolvedValue(undefined)

    const { rerender } = renderHook(
      ({ data }) =>
        useAutoSave({
          data,
          onSave,
          debounceMs: 2000,
          enabled: true,
        }),
      { initialProps: { data: { title: 'initial' } } }
    )

    // Trigger data change
    rerender({ data: { title: 'changed' } })

    // onSave should NOT be called immediately
    expect(onSave).not.toHaveBeenCalled()
  })

  it('saves after debounce period elapses', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined)

    const { rerender } = renderHook(
      ({ data }) =>
        useAutoSave({
          data,
          onSave,
          debounceMs: 1000,
          enabled: true,
        }),
      { initialProps: { data: { title: 'initial' } } }
    )

    // Change data to trigger debounce (first render is skipped by isFirstRender)
    rerender({ data: { title: 'updated' } })

    expect(onSave).not.toHaveBeenCalled()

    // Advance past the debounce period
    await act(async () => {
      vi.advanceTimersByTime(1100)
    })

    expect(onSave).toHaveBeenCalledTimes(1)
    expect(onSave).toHaveBeenCalledWith({ title: 'updated' })
  })

  it('skips save when disabled', async () => {
    const onSave = vi.fn().mockResolvedValue(undefined)

    const { rerender } = renderHook(
      ({ data, enabled }) =>
        useAutoSave({
          data,
          onSave,
          debounceMs: 500,
          enabled,
        }),
      { initialProps: { data: { title: 'initial' }, enabled: false } }
    )

    // Change data but with enabled = false
    rerender({ data: { title: 'changed' }, enabled: false })

    // Wait for well past the debounce period
    await act(async () => {
      vi.advanceTimersByTime(2000)
    })

    expect(onSave).not.toHaveBeenCalled()
  })

  it('sets error state on save failure', async () => {
    const onSave = vi.fn().mockRejectedValue(new Error('Network failure'))

    const { result, rerender } = renderHook(
      ({ data }) =>
        useAutoSave({
          data,
          onSave,
          debounceMs: 500,
          enabled: true,
        }),
      { initialProps: { data: { title: 'initial' } } }
    )

    // Change data to trigger debounce
    rerender({ data: { title: 'will-fail' } })

    // Advance past debounce
    await act(async () => {
      vi.advanceTimersByTime(600)
    })

    // Allow the rejected promise to settle
    await act(async () => {
      await vi.runAllTimersAsync()
    })

    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Network failure')
  })

  it('clearDraftBackup removes localStorage data', () => {
    const storageKey = 'draft-report-42'
    const onSave = vi.fn().mockResolvedValue(undefined)

    // Put some data in localStorage first
    localStorage.setItem(storageKey, JSON.stringify({ title: 'draft' }))

    const { result } = renderHook(() =>
      useAutoSave({
        data: { title: 'test' },
        onSave,
        debounceMs: 2000,
        enabled: true,
        storageKey,
      })
    )

    expect(localStorage.getItem(storageKey)).not.toBeNull()

    act(() => {
      result.current.clearDraftBackup()
    })

    expect(localStorage.getItem(storageKey)).toBeNull()
  })

  it('loadDraftBackup retrieves data from localStorage', () => {
    const storageKey = 'draft-report-99'
    const draftData = { title: 'Relatorio Rascunho', sections: [] }
    const onSave = vi.fn().mockResolvedValue(undefined)

    localStorage.setItem(storageKey, JSON.stringify(draftData))

    const { result } = renderHook(() =>
      useAutoSave({
        data: { title: '' },
        onSave,
        debounceMs: 2000,
        enabled: true,
        storageKey,
      })
    )

    const loaded = result.current.loadDraftBackup()
    expect(loaded).toEqual(draftData)
  })

  it('reports status as pending before debounce completes', () => {
    const onSave = vi.fn().mockResolvedValue(undefined)

    const { result, rerender } = renderHook(
      ({ data }) =>
        useAutoSave({
          data,
          onSave,
          debounceMs: 2000,
          enabled: true,
        }),
      { initialProps: { data: { title: 'initial' } } }
    )

    // Trigger data change
    rerender({ data: { title: 'changed' } })

    expect(result.current.status).toBe('pending')
    expect(result.current.isPending).toBe(true)
  })
})
