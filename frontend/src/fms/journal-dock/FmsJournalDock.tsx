import type { FmsDecision } from '../placeholder-feed/fms-placeholder-types'
import './fms-journal-dock.css'

type FmsJournalDockProps = {
  decisions: FmsDecision[]
  onOpenResult: (decision: FmsDecision) => void
}

export function FmsJournalDock({ decisions, onOpenResult }: FmsJournalDockProps) {
  const completed = decisions.filter((decision) => decision.state === 'recent')

  return (
    <section className="fms-journal-dock" aria-label="FMS Journal">
      <header>
        <div><small>Research ledger</small><h2>Journal</h2></div>
        <span>{completed.length} Trades</span>
      </header>
      <p className="fms-journal-notice">Empirical Trade Ledger · Derived from MT5 broker candles on H1 timeframe.</p>
      <div className="fms-journal-list">
        {completed.length === 0 ? (
          <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--text-faint)', fontSize: '0.8rem' }}>
            No evaluated trade ledger entries recorded.
          </div>
        ) : (
          completed.map((decision) => (
          <button type="button" key={decision.id} onClick={() => onOpenResult(decision)}>
            <span><strong>{decision.symbol}</strong><small>{decision.eventName}</small></span>
            <span className={decision.result === 'tp-reached' ? 'positive' : decision.result === 'sl-reached' ? 'negative' : ''}>
              {decision.resultR === null ? 'No trade' : `${decision.resultR > 0 ? '+' : ''}${decision.resultR.toFixed(2)}R`}
            </span>
          </button>
        )))}
      </div>
    </section>
  )
}
