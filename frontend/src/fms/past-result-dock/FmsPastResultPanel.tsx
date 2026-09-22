import type { FmsChartArrow, FmsDecision } from '../placeholder-feed/fms-placeholder-types'
import { formatAppTimestamp, type TimeDisplayPreference } from '../../appearance/time-display/time-display-preference'
import './fms-past-result-panel.css'

type SelectedFmsResult = FmsChartArrow | FmsDecision

type FmsPastResultPanelProps = { result: SelectedFmsResult | null; timeDisplay: TimeDisplayPreference }

function resultLabel(result: SelectedFmsResult) {
  if (result.resultR === null) return result.result === 'open' ? 'Pending' : 'No trade'
  return `${result.resultR > 0 ? '+' : ''}${result.resultR.toFixed(2)}R`
}

export function FmsPastResultPanel({ result, timeDisplay }: FmsPastResultPanelProps) {
  if (!result) {
    return <div className="fms-past-result-empty">Select an FMS arrow or result to inspect its verified audit record.</div>
  }

  return (
    <section className="fms-past-result-panel" aria-label="FMS Past Result">
      <div className="fms-result-summary">
        <small>Registered Setup Execution</small>
        <strong>{result.symbol} · {result.eventName}</strong>
        <span>{result.setupName}</span>
      </div>
      <dl>
        <div><dt>Version</dt><dd>FMS {result.version}</dd></div>
        <div><dt>Direction</dt><dd>{result.direction}</dd></div>
        <div><dt>Result</dt><dd>{resultLabel(result)}</dd></div>
        <div><dt>Release</dt><dd>{formatAppTimestamp(result.releaseTime, timeDisplay)}</dd></div>
      </dl>
      <div className="fms-result-note">
        <strong>Audit note</strong>
        <p>Codified quantitative setup verified under FMS Quality Gate (WR ≥ 50%, Net R &gt; 0, R:R ≥ 1.00).</p>
      </div>
    </section>
  )
}
