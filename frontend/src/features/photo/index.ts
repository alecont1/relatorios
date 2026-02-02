// Hooks
export { useCamera, useGeolocation, type GPSCoordinates } from './hooks'

// Components
export { CameraCapture, type CaptureMetadata } from './components/CameraCapture'

// API
export { photoApi, type PhotoMetadata, type PhotoListItem, type PhotoUploadData } from './api/photoApi'

// Utils
export { compressImage, addWatermark, processImage, generateThumbnail } from './utils/imageProcessor'
