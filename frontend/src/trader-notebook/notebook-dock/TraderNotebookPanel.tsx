import { useState } from 'react'
import type { SymbolQuote } from '../../market-data/contracts/SymbolQuote'
import './trader-notebook-panel.css'

export type PlannedTradeState = {
  direction: 'long' | 'short'
  entryPrice: number | null
  tpPrice: number | null
  slPrice: number | null
  showOnChart: boolean
}

type TraderNotebookPanelProps = {
  selectedSymbol: string
  quote: SymbolQuote | null
  plan: PlannedTradeState
  onPlanChange: (plan: PlannedTradeState) => void
}

export function TraderNotebookPanel({
  selectedSymbol,
  quote,
  plan,
  onPlanChange,
}: TraderNotebookPanelProps) {
  const [prevSymbol, setPrevSymbol] = useState(selectedSymbol)
  const [note, setNote] = useState<string>(() => {
    return localStorage.getItem(`trader_notebook_note_${selectedSymbol}`) || ''
  })
  const [saveStatus, setSaveStatus] = useState<string>('Saved')

  if (selectedSymbol !== prevSymbol) {
    setPrevSymbol(selectedSymbol)
    const saved = localStorage.getItem(`trader_notebook_note_${selectedSymbol}`)
    setNote(saved || '')
    setSaveStatus('Saved')
  }

  const handleNoteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    setNote(val)
    localStorage.setItem(`trader_notebook_note_${selectedSymbol}`, val)
    setSaveStatus('Auto-saved')
  }

  const handleSetMarketEntry = () => {
    if (!quote) return
    const currentPrice = plan.direction === 'long' ? quote.ask : quote.bid
    onPlanChange({
      ...plan,
      entryPrice: currentPrice,
    })
  }

  // Calculate pips and R:R
  const precision = quote?.precision ?? 5
  const pipMultiplier = precision === 3 || precision === 5 ? 10000 : 100
  const entry = plan.entryPrice
  const tp = plan.tpPrice
  const sl = plan.slPrice

  let tpPips: number | null = null
  let slPips: number | null = null
  let rrRatio: number | null = null

  if (entry != null && tp != null && sl != null && entry > 0 && tp > 0 && sl > 0) {
    if (plan.direction === 'long') {
      tpPips = (tp - entry) * pipMultiplier
      slPips = (entry - sl) * pipMultiplier
    } else {
      tpPips = (entry - tp) * pipMultiplier
      slPips = (sl - entry) * pipMultiplier
    }
    if (slPips > 0 && tpPips > 0) {
      rrRatio = tpPips / slPips
    }
  }

  return (
    <section className="trader-notebook-panel" aria-label="Trader Notebook & Execution Planner">
      {/* Col 1: Symbol & Planned Execution Levels */}
      <div className="notebook-col notebook-levels-col">
        <div className="notebook-col-header">
          <span className="notebook-eyebrow">Execution Plan</span>
          <label className="chart-projection-toggle">
            <input
              type="checkbox"
              checked={plan.showOnChart}
              onChange={(e) => onPlanChange({ ...plan, showOnChart: e.target.checked })}
            />
            <span>Project on Chart</span>
          </label>
        </div>

        <div className="notebook-symbol-strip">
          <strong className="notebook-symbol-title">{selectedSymbol}</strong>
          <div className="direction-toggle-group">
            <button
              type="button"
              className={`dir-toggle-btn buy ${plan.direction === 'long' ? 'active' : ''}`}
              onClick={() => onPlanChange({ ...plan, direction: 'long' })}
            >
              LONG (BUY)
            </button>
            <button
              type="button"
              className={`dir-toggle-btn sell ${plan.direction === 'short' ? 'active' : ''}`}
              onClick={() => onPlanChange({ ...plan, direction: 'short' })}
            >
              SHORT (SELL)
            </button>
          </div>
        </div>

        {/* Price Inputs */}
        <div className="levels-input-grid">
          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-entry">Entry Price</label>
              {quote && (
                <button type="button" className="set-market-btn" onClick={handleSetMarketEntry}>
                  Use Market ({plan.direction === 'long' ? quote.ask.toFixed(precision) : quote.bid.toFixed(precision)})
                </button>
              )}
            </div>
            <input
              id="plan-entry"
              type="number"
              step="any"
              placeholder="e.g. 1.10500"
              value={plan.entryPrice ?? ''}
              onChange={(e) =>
                onPlanChange({
                  ...plan,
                  entryPrice: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </div>

          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-tp">Take Profit</label>
              {tpPips != null && <span className="pips-badge positive">+{tpPips.toFixed(1)}p</span>}
            </div>
            <input
              id="plan-tp"
              type="number"
              step="any"
              placeholder="e.g. 1.11250"
              value={plan.tpPrice ?? ''}
              onChange={(e) =>
                onPlanChange({
                  ...plan,
                  tpPrice: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </div>

          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-sl">Stop Loss</label>
              {slPips != null && <span className="pips-badge negative">-{slPips.toFixed(1)}p</span>}
            </div>
            <input
              id="plan-sl"
              type="number"
              step="any"
              placeholder="e.g. 1.10000"
              value={plan.slPrice ?? ''}
              onChange={(e) =>
                onPlanChange({
                  ...plan,
                  slPrice: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </div>
        </div>
      </div>

      {/* Col 2: Risk / Reward & Calculation Summary */}
      <div className="notebook-col notebook-metrics-col">
        <div className="notebook-col-header">
          <span className="notebook-eyebrow">Risk / Reward Metrics</span>
          <span className="source-tag">Deterministic Math</span>
        </div>

        <div className="metrics-cards-grid">
          <div className="metric-card">
            <span className="metric-lbl">Target Reward</span>
            <strong className="metric-val text-green">
              {tpPips != null ? `+${tpPips.toFixed(1)} pips` : '—'}
            </strong>
            <small className="metric-sub">Distance to TP</small>
          </div>
          <div className="metric-card">
            <span className="metric-lbl">Max Risk</span>
            <strong className="metric-val text-rose">
              {slPips != null ? `-${slPips.toFixed(1)} pips` : '—'}
            </strong>
            <small className="metric-sub">Distance to SL</small>
          </div>
          <div className="metric-card highlight">
            <span className="metric-lbl">Reward : Risk</span>
            <strong className="metric-val text-cyan">
              {rrRatio != null ? `1 : ${rrRatio.toFixed(2)}` : '—'}
            </strong>
            <small className="metric-sub">{rrRatio != null ? `${rrRatio.toFixed(2)}R Multiple` : 'Set Entry, TP & SL'}</small>
          </div>
        </div>

        <div className="planner-guidance-box">
          <strong>Trading Discipline Checklist</strong>
          <ul>
            <li>Does this trade align with upcoming high-impact calendar releases?</li>
            <li>Is the stop loss protected behind market structure or significant liquidity?</li>
            <li>Is the planned reward-to-risk ratio at least 1.25R to maintain statistical expectancy?</li>
          </ul>
        </div>
      </div>

      {/* Col 3: Trader Forensic Journal & Observations */}
      <div className="notebook-col notebook-journal-col">
        <div className="notebook-col-header">
          <span className="notebook-eyebrow">Trader Journal &amp; Thesis</span>
          <span className="durability-tag">● {saveStatus}</span>
        </div>

        <div className="journal-textarea-container">
          <textarea
            className="journal-textarea"
            value={note}
            onChange={handleNoteChange}
            placeholder={`Type your trade thesis, catalyst observation, technical structure, or post-trade audit notes for ${selectedSymbol}...\n\nAll notes are automatically preserved locally and durable against browser refresh.`}
            aria-label="Trader journal note"
          />
        </div>

        <footer className="journal-col-footer">
          <span>Key: <code className="font-mono">{selectedSymbol}</code></span>
          <span className="durability-hint">Durable across refresh</span>
        </footer>
      </div>
    </section>
  )
}
