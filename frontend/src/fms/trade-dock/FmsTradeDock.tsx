import { useMemo, useState } from 'react'
import { formatAppTimestamp, type TimeDisplayPreference } from '../../appearance/time-display/time-display-preference'
import type { FmsDecision, FmsDecisionState } from '../placeholder-feed/fms-placeholder-types'
import './fms-trade-dock.css'

type FmsTradeDockProps = {
  decisions: FmsDecision[]
  timeDisplay: TimeDisplayPreference
  onOpenResult: (decision: FmsDecision) => void
  onGoToArrow: (decision: FmsDecision) => void
}

const tabs: { id: FmsDecisionState; label: string }[] = [
  { id: 'upcoming', label: 'Upcoming' },
  { id: 'current', label: 'Current' },
  { id: 'recent', label: 'Recent' },
]

export function FmsTradeDock({ decisions, timeDisplay, onOpenResult, onGoToArrow }: FmsTradeDockProps) {
  const [activeState, setActiveState] = useState<FmsDecisionState>('upcoming')
  const visibleDecisions = useMemo(
    () => decisions.filter((decision) => decision.state === activeState),
    [activeState, decisions],
  )

  return (
    <section className="fms-trade-dock" aria-label="FMS Trade dock">
      <div className="fms-preview-banner">
        <strong>FMS Decadal Execution</strong>
        <span>34 Registered Setups · Quality Gate Verified</span>
      </div>
      <div className="fms-trade-tabs" role="tablist" aria-label="Trade state">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={activeState === tab.id ? 'active' : ''}
            onClick={() => setActiveState(tab.id)}
          >
            {tab.label} <span>{decisions.filter((item) => item.state === tab.id).length}</span>
          </button>
        ))}
      </div>
      <div className="fms-decision-list">
        {visibleDecisions.map((decision) => (
          <article className="fms-decision-card" key={decision.id}>
            <header>
              <strong>{decision.symbol}</strong>
              <span className={`fms-version ${decision.version}`}>FMS {decision.version}</span>
            </header>
            <h3>{decision.eventName}</h3>
            <p>{decision.setupName} · {decision.direction}</p>
            <time dateTime={new Date(decision.releaseTime).toISOString()}>{formatAppTimestamp(decision.releaseTime, timeDisplay)}</time>
            <div className="fms-card-actions">
              <button type="button" onClick={() => onOpenResult(decision)}>Past result</button>
              {activeState === 'recent' && (
                <button type="button" onClick={() => onGoToArrow(decision)}>Go to arrow</button>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
