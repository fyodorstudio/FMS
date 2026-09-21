export type FloatingToolbarPosition = { x: number; y: number }

const storageKey = 'fyodor.drawing-toolbar-position.v1'
const fallbackPosition: FloatingToolbarPosition = { x: 14, y: 14 }

export function readFloatingToolbarPosition(): FloatingToolbarPosition {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(storageKey) ?? '{}') as Partial<FloatingToolbarPosition>
    return typeof parsed.x === 'number' && typeof parsed.y === 'number'
      ? { x: Math.max(0, parsed.x), y: Math.max(0, parsed.y) }
      : fallbackPosition
  } catch {
    return fallbackPosition
  }
}

export function saveFloatingToolbarPosition(position: FloatingToolbarPosition) {
  try {
    window.localStorage.setItem(storageKey, JSON.stringify(position))
  } catch {
    // The toolbar remains movable for this session when storage is unavailable.
  }
}
