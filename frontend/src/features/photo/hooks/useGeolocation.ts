import { useState, useCallback, useEffect } from 'react'

export interface GPSCoordinates {
  latitude: number
  longitude: number
  accuracy: number
}

interface GeolocationState {
  coordinates: GPSCoordinates | null
  error: string | null
  isLoading: boolean
  isSupported: boolean
}

interface UseGeolocationOptions {
  enableHighAccuracy?: boolean
  timeout?: number
  maximumAge?: number
  watchPosition?: boolean
}

export function useGeolocation(options: UseGeolocationOptions = {}) {
  const {
    enableHighAccuracy = true,
    timeout = 10000,
    maximumAge = 0,
    watchPosition = false,
  } = options

  const [state, setState] = useState<GeolocationState>({
    coordinates: null,
    error: null,
    isLoading: false,
    isSupported: typeof navigator !== 'undefined' && 'geolocation' in navigator,
  })

  const getCurrentPosition = useCallback(async (): Promise<GPSCoordinates | null> => {
    if (!state.isSupported) {
      setState(prev => ({ ...prev, error: 'Geolocation not supported' }))
      return null
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }))

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords: GPSCoordinates = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          }
          setState({
            coordinates: coords,
            error: null,
            isLoading: false,
            isSupported: true,
          })
          resolve(coords)
        },
        (error) => {
          let errorMessage = 'Unknown error'
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Permissao de localizacao negada'
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Localizacao indisponivel'
              break
            case error.TIMEOUT:
              errorMessage = 'Tempo esgotado ao obter localizacao'
              break
          }
          setState(prev => ({
            ...prev,
            error: errorMessage,
            isLoading: false,
          }))
          resolve(null)
        },
        {
          enableHighAccuracy,
          timeout,
          maximumAge,
        }
      )
    })
  }, [state.isSupported, enableHighAccuracy, timeout, maximumAge])

  // Watch position if enabled
  useEffect(() => {
    if (!watchPosition || !state.isSupported) return

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        setState(prev => ({
          ...prev,
          coordinates: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
          },
          error: null,
        }))
      },
      (error) => {
        setState(prev => ({
          ...prev,
          error: error.message,
        }))
      },
      {
        enableHighAccuracy,
        timeout,
        maximumAge,
      }
    )

    return () => {
      navigator.geolocation.clearWatch(watchId)
    }
  }, [watchPosition, state.isSupported, enableHighAccuracy, timeout, maximumAge])

  return {
    ...state,
    getCurrentPosition,
  }
}
