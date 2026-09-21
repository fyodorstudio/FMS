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
        <span>Sample</span>
      </header>
      <p className="fms-journal-notice">This shell previews where immutable results and audit notes will live. Values are not research evidence.</p>
      <div className="fms-journal-list">
        {completed.map((decision) => (
          <button type="button" key={decision.id} onClick={() => onOpenResult(decision)}>
            <span><strong>{decision.symbol}</strong><small>{decision.eventName}</small></span>
            <span className={decision.result === 'tp-reached' ? 'positive' : decision.result === 'sl-reached' ? 'negative' : ''}>
              {decision.resultR === null ? 'No trade' : `${decision.resultR > 0 ? '+' : ''}${decision.resultR.toFixed(2)}R`}
            </span>
          </button>
        ))}
      </div>
    </section>
  )
}
