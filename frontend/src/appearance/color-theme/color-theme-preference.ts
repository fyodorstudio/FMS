export type ColorTheme = 'light' | 'dark'

const storageKey = 'fyodor.color-theme'

export function readColorTheme(): ColorTheme {
  try {
    return window.localStorage.getItem(storageKey) === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

export function applyColorTheme(theme: ColorTheme) {
  document.documentElement.dataset.theme = theme
  document.documentElement.style.colorScheme = theme

  try {
    window.localStorage.setItem(storageKey, theme)
  } catch {
    // The selected theme still applies for this session when storage is unavailable.
  }
}
