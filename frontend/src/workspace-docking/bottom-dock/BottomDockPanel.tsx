import type { ReactNode } from 'react'
import type { BottomDockWindow } from './bottom-dock-window'
import './bottom-dock-panel.css'

type BottomDockPanelProps = {
  activeWindow: BottomDockWindow
  activityCount: number
  hasPastResult: boolean
  onSelectWindow: (window: BottomDockWindow) => void
  onClose: () => void
  children: ReactNode
}

export function BottomDockPanel({
  activeWindow,
  activityCount,
  hasPastResult,
  onSelectWindow,
  onClose,
  children,
}: BottomDockPanelProps) {
  return (
    <section className="bottom-dock" aria-label="Bottom dock">
      <header className="bottom-dock-tabs">
        <button
          type="button"
          className={activeWindow === 'past-result' ? 'active' : ''}
          onClick={() => onSelectWindow('past-result')}
        >
          Past Result <span>{hasPastResult ? '1 selected' : 'Empty'}</span>
        </button>
        <button
          type="button"
          className={activeWindow === 'calendar' ? 'active' : ''}
          onClick={() => onSelectWindow('calendar')}
        >
          Economic Calendar <span>Preview</span>
        </button>
        <button
          type="button"
          className={activeWindow === 'activity' ? 'active' : ''}
          onClick={() => onSelectWindow('activity')}
        >
          Activity <span>{activityCount}</span>
        </button>
        <button className="bottom-dock-close" type="button" onClick={onClose} aria-label="Close bottom dock">
          ×
        </button>
      </header>
      <div className="bottom-dock-content">{children}</div>
    </section>
  )
}
