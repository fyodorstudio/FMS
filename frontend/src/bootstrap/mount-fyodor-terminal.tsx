import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../appearance/color-theme/color-theme-tokens.css'
import '../styles/global.css'
import { ActivityLogProvider } from '../system-observability/activity-log/activity-log-store'
import { FyodorTerminalShell } from '../terminal-shell/FyodorTerminalShell'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ActivityLogProvider>
      <FyodorTerminalShell />
    </ActivityLogProvider>
  </StrictMode>,
)
