export type LeftDockWindow = 'markets' | 'trade' | 'journal' | 'setups'

const storageKey = 'fyodor.left-dock.window.v1'

export function readLeftDockWindow(): LeftDockWindow {
  const stored = globalThis.localStorage?.getItem(storageKey)
  return stored === 'trade' || stored === 'journal' || stored === 'setups' ? stored : 'markets'
}

export function saveLeftDockWindow(window: LeftDockWindow) {
  globalThis.localStorage?.setItem(storageKey, window)
}
