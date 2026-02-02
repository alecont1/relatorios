import { useState, useCallback, useRef } from 'react'

interface UseCameraOptions {
  facingMode?: 'user' | 'environment'
}

interface CameraState {
  isActive: boolean
  error: string | null
  stream: MediaStream | null
}

export function useCamera(options: UseCameraOptions = {}) {
  const { facingMode = 'environment' } = options

  const [state, setState] = useState<CameraState>({
    isActive: false,
    error: null,
    stream: null,
  })

  const videoRef = useRef<HTMLVideoElement | null>(null)

  const startCamera = useCallback(async (videoElement: HTMLVideoElement) => {
    try {
      setState(prev => ({ ...prev, error: null }))

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
        audio: false,
      })

      videoElement.srcObject = stream
      await videoElement.play()

      videoRef.current = videoElement
      setState({
        isActive: true,
        error: null,
        stream,
      })

      return stream
    } catch (error) {
      let errorMessage = 'Erro ao acessar camera'
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = 'Permissao de camera negada'
        } else if (error.name === 'NotFoundError') {
          errorMessage = 'Camera nao encontrada'
        } else if (error.name === 'NotReadableError') {
          errorMessage = 'Camera em uso por outro aplicativo'
        }
      }
      setState(prev => ({ ...prev, error: errorMessage }))
      return null
    }
  }, [facingMode])

  const stopCamera = useCallback(() => {
    if (state.stream) {
      state.stream.getTracks().forEach(track => track.stop())
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setState({
      isActive: false,
      error: null,
      stream: null,
    })
  }, [state.stream])

  const capturePhoto = useCallback(async (): Promise<Blob | null> => {
    if (!videoRef.current || !state.isActive) {
      return null
    }

    const video = videoRef.current
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext('2d')
    if (!ctx) return null

    ctx.drawImage(video, 0, 0)

    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => resolve(blob),
        'image/jpeg',
        0.92
      )
    })
  }, [state.isActive])

  const switchCamera = useCallback(async () => {
    if (state.stream) {
      state.stream.getTracks().forEach(track => track.stop())
    }

    const newFacingMode = facingMode === 'environment' ? 'user' : 'environment'

    if (videoRef.current) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: newFacingMode,
            width: { ideal: 1920 },
            height: { ideal: 1080 },
          },
          audio: false,
        })

        videoRef.current.srcObject = stream
        await videoRef.current.play()

        setState(prev => ({
          ...prev,
          stream,
        }))

        return stream
      } catch {
        // Ignore switch errors
      }
    }

    return null
  }, [facingMode, state.stream])

  return {
    ...state,
    startCamera,
    stopCamera,
    capturePhoto,
    switchCamera,
  }
}
