import { ColorThemeButton } from '../appearance/color-theme/ColorThemeButton'
import type { ColorTheme } from '../appearance/color-theme/color-theme-preference'
import type { ChartTimeframe } from '../market-data/contracts/ChartTimeframe'
import type { BottomDockWindow } from '../workspace-docking/bottom-dock/bottom-dock-window'

type TerminalStatusBarProps = {
  sourceSymbolCount: number
  selectedSymbol: string
  timeframe: ChartTimeframe
  barCount: number
  activityCount: number
  bottomDockWindow: BottomDockWindow | null
  settingsOpen: boolean
  onToggleBottomDock: (window: BottomDockWindow) => void
  onThemeChanged: (theme: ColorTheme) => void
  onToggleSettings: () => void
}

export function TerminalStatusBar({
  sourceSymbolCount,
  selectedSymbol,
  timeframe,
  barCount,
  activityCount,
  bottomDockWindow,
  settingsOpen,
  onToggleBottomDock,
  onThemeChanged,
  onToggleSettings,
}: TerminalStatusBarProps) {
  return (
    <footer className="status-bar">
      <span className="status-message"><i className="status-dot" /> Sample source · {sourceSymbolCount} symbols</span>
      <span className="status-selection">{selectedSymbol} · {timeframe} · {barCount} bars</span>
      <div className="status-actions">
        <button className={`status-action${bottomDockWindow === 'activity' ? ' active' : ''}`} type="button" onClick={() => onToggleBottomDock('activity')} aria-expanded={bottomDockWindow === 'activity'}>
          Activity <span className="activity-count">{activityCount}</span>
        </button>
        <button className={`status-action${bottomDockWindow === 'calendar' ? ' active' : ''}`} type="button" onClick={() => onToggleBottomDock('calendar')} aria-expanded={bottomDockWindow === 'calendar'}>
          Calendar <span className="preview-label">Sample</span>
        </button>
        <ColorThemeButton onThemeChanged={onThemeChanged} />
        <button className={`status-action${settingsOpen ? ' active' : ''}`} type="button" onClick={onToggleSettings} aria-expanded={settingsOpen}>
          <span aria-hidden="true">⚙</span> Settings
        </button>
      </div>
    </footer>
  )
}
