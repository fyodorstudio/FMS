import { useState } from 'react'
import { applyColorTheme, readColorTheme, type ColorTheme } from './color-theme-preference'

type ColorThemeButtonProps = {
  onThemeChanged: (theme: ColorTheme) => void
}

export function ColorThemeButton({ onThemeChanged }: ColorThemeButtonProps) {
  const [theme, setTheme] = useState<ColorTheme>(() => {
    const initialTheme = readColorTheme()
    applyColorTheme(initialTheme)
    return initialTheme
  })

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light'
    applyColorTheme(nextTheme)
    setTheme(nextTheme)
    onThemeChanged(nextTheme)
  }

  return (
    <button
      className="status-action"
      type="button"
      onClick={toggleTheme}
      aria-label={`Use ${theme === 'light' ? 'dark' : 'light'} theme`}
      title={`Use ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      <span aria-hidden="true">{theme === 'light' ? '☀' : '☾'}</span>
      {theme === 'light' ? 'Light' : 'Dark'}
    </button>
  )
}
