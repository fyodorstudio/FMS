import type { FmsChartArrow, FmsDecision } from '../placeholder-feed/fms-placeholder-types'
import './fms-past-result-panel.css'

type SelectedFmsResult = FmsChartArrow | FmsDecision

type FmsPastResultPanelProps = { result: SelectedFmsResult | null }

function resultLabel(result: SelectedFmsResult) {
  if (result.resultR === null) return result.result === 'open' ? 'Pending' : 'No trade'
  return `${result.resultR > 0 ? '+' : ''}${result.resultR.toFixed(2)}R`
}

export function FmsPastResultPanel({ result }: FmsPastResultPanelProps) {
  if (!result) {
    return <div className="fms-past-result-empty">Select an FMS arrow or result to inspect its placeholder record.</div>
  }

  return (
    <section className="fms-past-result-panel" aria-label="FMS Past Result">
      <div className="fms-result-summary">
        <small>Placeholder record</small>
        <strong>{result.symbol} · {result.eventName}</strong>
        <span>{result.setupName}</span>
      </div>
      <dl>
        <div><dt>Version</dt><dd>FMS {result.version}</dd></div>
        <div><dt>Direction</dt><dd>{result.direction}</dd></div>
        <div><dt>Result</dt><dd>{resultLabel(result)}</dd></div>
        <div><dt>Release</dt><dd>{result.releaseLabel}</dd></div>
      </dl>
      <div className="fms-result-note">
        <strong>Audit note</strong>
        <p>Notes and immutable research evidence are deliberately not implemented in this placeholder shell.</p>
      </div>
    </section>
  )
}
