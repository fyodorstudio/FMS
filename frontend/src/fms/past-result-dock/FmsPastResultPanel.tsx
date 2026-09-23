import { useState } from 'react'
import type { FmsChartArrow, FmsDecision } from '../placeholder-feed/fms-placeholder-types'
import { formatAppTimestamp, type TimeDisplayPreference } from '../../appearance/time-display/time-display-preference'
import './fms-past-result-panel.css'

type SelectedFmsResult = FmsChartArrow | FmsDecision

type FmsPastResultPanelProps = {
  result: SelectedFmsResult | null
  timeDisplay: TimeDisplayPreference
}

function resultStatusBadge(result: SelectedFmsResult) {
  if (result.resultR === null) {
    return {
      label: result.result === 'open' ? 'Position Open' : 'No Trade',
      className: 'pending',
    }
  }
  if (result.resultR > 0) {
    return {
      label: `+${result.resultR.toFixed(2)}R (TP Reached)`,
      className: 'win',
    }
  }
  return {
    label: `${result.resultR.toFixed(2)}R (SL Reached)`,
    className: 'loss',
  }
}

export function FmsPastResultPanel({ result, timeDisplay }: FmsPastResultPanelProps) {
  const resultId = result?.id
  const [prevResultId, setPrevResultId] = useState<string | undefined>(resultId)
  const [auditNote, setAuditNote] = useState<string>(() => {
    if (!resultId) return ''
    return localStorage.getItem(`fms_audit_note_${resultId}`) || ''
  })
  const [saveStatus, setSaveStatus] = useState<string>('Saved')

  if (resultId !== prevResultId) {
    setPrevResultId(resultId)
    const saved = resultId ? localStorage.getItem(`fms_audit_note_${resultId}`) : ''
    setAuditNote(saved || '')
    setSaveStatus('Saved')
  }

  const handleNoteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const nextVal = e.target.value
    setAuditNote(nextVal)
    if (resultId) {
      const storageKey = `fms_audit_note_${resultId}`
      localStorage.setItem(storageKey, nextVal)
      setSaveStatus('Auto-saved')
    }
  }

  if (!result) {
    return (
      <div className="fms-past-result-empty">
        <div className="empty-message-wrap">
          <span className="empty-icon">◈</span>
          <strong>No Arrow Selected</strong>
          <p>Select any setup arrow on the chart or from the Past Arrows dropdown to inspect verified levels, rationale, and manual audit log.</p>
        </div>
      </div>
    )
  }

  const badge = resultStatusBadge(result)
  const isBuy = result.direction === 'long'
  const directionLabel = isBuy ? 'LONG / BUY' : 'SHORT / SELL'
  const methodCode = result.method || (result.setupName ? result.setupName.split(' ')[0] : 'M-MSD')
  const entryPrice = result.entryPrice ?? result.price

  return (
    <section className="fms-past-result-panel" aria-label="FMS Past Result Audit Panel">
      {/* 1. Setup Identity & Catalyst Section */}
      <div className="fms-result-col fms-identity-col">
        <div className="fms-col-header">
          <span className="fms-eyebrow">Codified Quantitative Setup</span>
          <span className={`fms-method-badge method-${methodCode.replace('M-', '').toLowerCase()}`}>
            {methodCode}
          </span>
        </div>

        <div className="fms-instrument-title">
          <strong className="fms-pair-text">{result.symbol}</strong>
          <span className="fms-event-text">{result.eventName || result.setupName}</span>
        </div>

        <div className="fms-meta-specs">
          <div className="fms-meta-item">
            <span className="meta-lbl">Direction</span>
            <span className={`direction-chip ${isBuy ? 'buy' : 'sell'}`}>{directionLabel}</span>
          </div>
          <div className="fms-meta-item">
            <span className="meta-lbl">Outcome</span>
            <span className={`outcome-chip ${badge.className}`}>{badge.label}</span>
          </div>
          <div className="fms-meta-item">
            <span className="meta-lbl">Release Time</span>
            <span className="meta-val">{formatAppTimestamp(result.releaseTime, timeDisplay)}</span>
          </div>
          <div className="fms-meta-item">
            <span className="meta-lbl">Signal ID</span>
            <span className="meta-val font-mono">{result.id.slice(0, 18)}...</span>
          </div>
        </div>
      </div>

      {/* 2. Execution Price Levels & Setup Rationale */}
      <div className="fms-result-col fms-execution-col">
        <div className="fms-col-header">
          <span className="fms-eyebrow">Execution Levels &amp; Catalyst Rationale</span>
          <span className="fms-source-tag">100% Empirical MT5</span>
        </div>

        {/* Level metrics strip */}
        <div className="fms-levels-grid">
          <div className="fms-level-card level-entry">
            <span className="level-lbl">Entry Price</span>
            <strong className="level-val">{entryPrice ? entryPrice.toFixed(5) : '—'}</strong>
            <small className="level-sub">At Signal Bar</small>
          </div>
          <div className="fms-level-card level-tp">
            <span className="level-lbl">Take Profit</span>
            <strong className="level-val text-green">
              {result.tpPrice ? result.tpPrice.toFixed(5) : '—'}
            </strong>
            <small className="level-sub">
              {result.recommendedTpPips ? `+${result.recommendedTpPips.toFixed(0)}p (+1.25R)` : '+1.25R Target'}
            </small>
          </div>
          <div className="fms-level-card level-sl">
            <span className="level-lbl">Stop Loss</span>
            <strong className="level-val text-rose">
              {result.slPrice ? result.slPrice.toFixed(5) : '—'}
            </strong>
            <small className="level-sub">
              {result.recommendedSlPips ? `-${result.recommendedSlPips.toFixed(0)}p (-1.00R)` : '-1.00R Stop'}
            </small>
          </div>
        </div>

        {/* Why this arrow appeared (Setup Rationale) */}
        <div className="fms-rationale-box">
          <div className="rationale-header">
            <strong>Setup Trigger Rationale</strong>
            <span className="rationale-sub">Forensic Catalyst Deviation</span>
          </div>
          <p className="rationale-body">
            {result.reason ||
              `Signal generated under strategy ${methodCode} on ${result.symbol}. Macroeconomic catalyst release ${result.eventName} triggered deviation criteria surpassing minimum Z-score threshold. Trade path evaluated against subsequent bar price action for TP (+1.25R) vs SL (-1.00R).`}
          </p>
        </div>
      </div>

      {/* 3. Interactive, Durable Audit Note */}
      <div className="fms-result-col fms-audit-col">
        <div className="fms-col-header">
          <span className="fms-eyebrow">Trader Audit Findings</span>
          <span className="fms-durability-pill" title="Saved directly into localStorage">
            ● {saveStatus}
          </span>
        </div>

        <div className="audit-textarea-wrap">
          <textarea
            className="audit-note-textarea"
            value={auditNote}
            onChange={handleNoteChange}
            placeholder="Type your manual audit findings, candle price action notes, or execution observations for this arrow (automatically saved across browser refresh)..."
            aria-label="Audit findings note"
          />
        </div>

        <footer className="audit-col-footer">
          <span>Note key: <code className="font-mono">{result.id.slice(0, 16)}</code></span>
          <span className="durability-hint">Durable against refresh</span>
        </footer>
      </div>
    </section>
  )
}
