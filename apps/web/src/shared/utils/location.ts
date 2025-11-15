export const LOCATION_CHANGE_EVENT = 'app-location-change'

export const notifyLocationChange = (): void => {
  if (typeof window === 'undefined') {
    return
  }
  window.dispatchEvent(new Event(LOCATION_CHANGE_EVENT))
}

