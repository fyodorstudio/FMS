import type { FmsDecision, FmsRegisteredSetup } from '../../fms/placeholder-feed/fms-placeholder-types'
import { FmsJournalDock } from '../../fms/journal-dock/FmsJournalDock'
import { RegisteredSetupDock } from '../../fms/registered-setup-dock/RegisteredSetupDock'
import { FmsTradeDock } from '../../fms/trade-dock/FmsTradeDock'
import type { SymbolQuote } from '../../market-data/contracts/SymbolQuote'
import { MarketWatchPanel } from '../../market-data/market-watch/MarketWatchPanel'
import type { LeftDockWindow } from './left-dock-window'
import './left-dock-panel.css'

type LeftDockPanelProps = {
  activeWindow: LeftDockWindow
  symbols: SymbolQuote[]
  selectedSymbol: string
  decisions: FmsDecision[]
  setups: FmsRegisteredSetup[]
  onSelectWindow: (window: LeftDockWindow) => void
  onSelectSymbol: (symbol: string) => void
  onOpenResult: (decision: FmsDecision) => void
  onGoToArrow: (decision: FmsDecision) => void
}

const tabs: { id: LeftDockWindow; label: string }[] = [
  { id: 'markets', label: 'Markets' },
  { id: 'trade', label: 'Trade' },
  { id: 'journal', label: 'Journal' },
  { id: 'setups', label: 'Setups' },
]

export function LeftDockPanel({
  activeWindow,
  symbols,
  selectedSymbol,
  decisions,
  setups,
  onSelectWindow,
  onSelectSymbol,
  onOpenResult,
  onGoToArrow,
}: LeftDockPanelProps) {
  return (
    <aside className="left-dock" aria-label="Left workspace dock">
      <nav className="left-dock-tabs" aria-label="Left dock windows">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={activeWindow === tab.id ? 'active' : ''}
            onClick={() => onSelectWindow(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>
      <div className="left-dock-content">
        {activeWindow === 'markets' && (
          <MarketWatchPanel symbols={symbols} selectedSymbol={selectedSymbol} onSelect={onSelectSymbol} />
        )}
        {activeWindow === 'trade' && (
          <FmsTradeDock decisions={decisions} onOpenResult={onOpenResult} onGoToArrow={onGoToArrow} />
        )}
        {activeWindow === 'journal' && <FmsJournalDock decisions={decisions} onOpenResult={onOpenResult} />}
        {activeWindow === 'setups' && <RegisteredSetupDock setups={setups} />}
      </div>
    </aside>
  )
}
