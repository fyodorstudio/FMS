import { useMemo, useState } from 'react'
import type { SymbolQuote } from '../../market-data/contracts/SymbolQuote'
import {
  getPipMultiplier,
  type PlannedTradeState,
  type RegisteredTradeArrow,
} from '../contracts/trader-notebook-types'
import './trader-notebook-panel.css'

type TraderNotebookPanelProps = {
  selectedSymbol: string
  quote: SymbolQuote | null
  latestBarTime: number
  plan: PlannedTradeState
  registeredArrows: RegisteredTradeArrow[]
  selectedArrowId: string | null
  onPlanChange: (plan: PlannedTradeState) => void
  onSelectArrowId: (id: string | null) => void
  onRegisterArrow: (arrow: Omit<RegisteredTradeArrow, 'id' | 'createdAt'>) => void
  onDeleteArrow: (id: string) => void
}

export function TraderNotebookPanel({
  selectedSymbol,
  quote,
  latestBarTime,
  plan,
  registeredArrows,
  selectedArrowId,
  onPlanChange,
  onSelectArrowId,
  onRegisterArrow,
  onDeleteArrow,
}: TraderNotebookPanelProps) {
  const [prevSymbol, setPrevSymbol] = useState(selectedSymbol)
  const [note, setNote] = useState<string>(() => {
    return localStorage.getItem(`trader_notebook_note_${selectedSymbol}`) || ''
  })
  const [saveStatus, setSaveStatus] = useState<string>('Saved')
  const [regSuccessMsg, setRegSuccessMsg] = useState<string | null>(null)

  // Handle symbol change
  if (selectedSymbol !== prevSymbol) {
    setPrevSymbol(selectedSymbol)
    const saved = localStorage.getItem(`trader_notebook_note_${selectedSymbol}`)
    setNote(saved || '')
    setSaveStatus('Saved')
    setRegSuccessMsg(null)
  }

  const handleNoteChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value
    setNote(val)
    localStorage.setItem(`trader_notebook_note_${selectedSymbol}`, val)
    setSaveStatus('Auto-saved')
  }

  const precision = quote?.precision ?? 5
  const pipMultiplier = useMemo(() => getPipMultiplier(selectedSymbol, precision), [selectedSymbol, precision])

  // Derive current values from draft plan or selected registered arrow
  const selectedArrow = useMemo(() => {
    return selectedArrowId ? registeredArrows.find((a) => a.id === selectedArrowId) ?? null : null
  }, [registeredArrows, selectedArrowId])

  const direction = selectedArrow ? selectedArrow.direction : plan.direction
  const entryPrice = selectedArrow ? selectedArrow.entryPrice : plan.entryPrice
  const tpPrice = selectedArrow ? selectedArrow.tpPrice : plan.tpPrice
  const slPrice = selectedArrow ? selectedArrow.slPrice : plan.slPrice

  // Calculate pips and R:R
  const calculatedMetrics = useMemo(() => {
    let tpPips: number | null = null
    let slPips: number | null = null
    let rrRatio: number | null = null

    if (entryPrice != null && entryPrice > 0) {
      if (tpPrice != null && tpPrice > 0) {
        tpPips = direction === 'long'
          ? (tpPrice - entryPrice) * pipMultiplier
          : (entryPrice - tpPrice) * pipMultiplier
      }
      if (slPrice != null && slPrice > 0) {
        slPips = direction === 'long'
          ? (entryPrice - slPrice) * pipMultiplier
          : (slPrice - entryPrice) * pipMultiplier
      }
      if (tpPips != null && slPips != null && slPips > 0) {
        rrRatio = tpPips / slPips
      }
    }
    return { tpPips, slPips, rrRatio }
  }, [direction, entryPrice, pipMultiplier, slPrice, tpPrice])

  // Bi-directional input handlers for Draft Plan
  const handleEntryChange = (valStr: string) => {
    const nextEntry = valStr ? Number(valStr) : null
    onPlanChange({ ...plan, entryPrice: nextEntry })
    onSelectArrowId(null)
  }

  const handleUseMarketPrice = () => {
    if (!quote) return
    const currentPrice = plan.direction === 'long' ? quote.ask : quote.bid
    onPlanChange({ ...plan, entryPrice: currentPrice })
    onSelectArrowId(null)
  }

  const handleSlPriceChange = (valStr: string) => {
    const nextSl = valStr ? Number(valStr) : null
    onPlanChange({ ...plan, slPrice: nextSl })
    onSelectArrowId(null)
  }

  const handleSlPipsChange = (pipsStr: string) => {
    if (!pipsStr || plan.entryPrice == null) {
      onPlanChange({ ...plan, slPrice: null })
      return
    }
    const pips = Number(pipsStr)
    const priceDelta = pips / pipMultiplier
    const nextSl = plan.direction === 'long' ? plan.entryPrice - priceDelta : plan.entryPrice + priceDelta
    onPlanChange({ ...plan, slPrice: Number(nextSl.toFixed(precision)) })
    onSelectArrowId(null)
  }

  const handleTpPriceChange = (valStr: string) => {
    const nextTp = valStr ? Number(valStr) : null
    onPlanChange({ ...plan, tpPrice: nextTp })
    onSelectArrowId(null)
  }

  const handleTpPipsChange = (pipsStr: string) => {
    if (!pipsStr || plan.entryPrice == null) {
      onPlanChange({ ...plan, tpPrice: null })
      return
    }
    const pips = Number(pipsStr)
    const priceDelta = pips / pipMultiplier
    const nextTp = plan.direction === 'long' ? plan.entryPrice + priceDelta : plan.entryPrice - priceDelta
    onPlanChange({ ...plan, tpPrice: Number(nextTp.toFixed(precision)) })
    onSelectArrowId(null)
  }

  const handleTargetRrChange = (rrTarget: number) => {
    if (plan.entryPrice == null || calculatedMetrics.slPips == null || calculatedMetrics.slPips <= 0) return
    const desiredTpPips = calculatedMetrics.slPips * rrTarget
    const priceDelta = desiredTpPips / pipMultiplier
    const nextTp = plan.direction === 'long' ? plan.entryPrice + priceDelta : plan.entryPrice - priceDelta
    onPlanChange({ ...plan, tpPrice: Number(nextTp.toFixed(precision)) })
    onSelectArrowId(null)
  }

  // Register Arrow Handler
  const canRegister =
    entryPrice != null &&
    entryPrice > 0 &&
    tpPrice != null &&
    tpPrice > 0 &&
    slPrice != null &&
    slPrice > 0 &&
    calculatedMetrics.tpPips != null &&
    calculatedMetrics.slPips != null &&
    calculatedMetrics.rrRatio != null &&
    calculatedMetrics.tpPips > 0 &&
    calculatedMetrics.slPips > 0

  const handleRegisterClick = () => {
    if (!canRegister) return
    onRegisterArrow({
      symbol: selectedSymbol,
      time: latestBarTime || Math.floor(Date.now() / 1000),
      direction,
      entryPrice: entryPrice!,
      tpPrice: tpPrice!,
      slPrice: slPrice!,
      tpPips: calculatedMetrics.tpPips!,
      slPips: calculatedMetrics.slPips!,
      rrRatio: calculatedMetrics.rrRatio!,
      note,
    })
    setRegSuccessMsg(`✓ Registered ${direction.toUpperCase()} setup arrow on chart!`)
    setTimeout(() => setRegSuccessMsg(null), 4000)
  }

  return (
    <section className="trader-notebook-panel" aria-label="Trader Notebook & Execution Planner">
      {/* Col 1: Execution Plan & Bi-directional Calculator */}
      <div className="notebook-col notebook-levels-col">
        <div className="notebook-col-header">
          <span className="notebook-eyebrow">
            {selectedArrow ? 'Selected Registered Setup' : 'Draft Execution Plan'}
          </span>
          {!selectedArrow && (
            <label className="chart-projection-toggle" title="Show horizontal lines on chart">
              <input
                type="checkbox"
                checked={plan.showOnChart}
                onChange={(e) => onPlanChange({ ...plan, showOnChart: e.target.checked })}
              />
              <span>Project on Chart</span>
            </label>
          )}
        </div>

        {/* Symbol & Direction Buttons */}
        <div className="notebook-symbol-strip">
          <strong className="notebook-symbol-title">{selectedSymbol}</strong>
          <div className="direction-toggle-group">
            <button
              type="button"
              className={`dir-toggle-btn buy ${direction === 'long' ? 'active' : ''}`}
              onClick={() => {
                onPlanChange({ ...plan, direction: 'long' })
                onSelectArrowId(null)
              }}
              disabled={Boolean(selectedArrow)}
            >
              LONG (BUY)
            </button>
            <button
              type="button"
              className={`dir-toggle-btn sell ${direction === 'short' ? 'active' : ''}`}
              onClick={() => {
                onPlanChange({ ...plan, direction: 'short' })
                onSelectArrowId(null)
              }}
              disabled={Boolean(selectedArrow)}
            >
              SHORT (SELL)
            </button>
          </div>
        </div>

        {/* Inputs Grid */}
        <div className="levels-input-grid">
          {/* Entry Price */}
          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-entry">Entry Price</label>
              {quote && !selectedArrow && (
                <button type="button" className="set-market-btn" onClick={handleUseMarketPrice}>
                  Use Market ({direction === 'long' ? quote.ask.toFixed(precision) : quote.bid.toFixed(precision)})
                </button>
              )}
            </div>
            <input
              id="plan-entry"
              type="number"
              step="any"
              placeholder="e.g. 1.10500"
              value={entryPrice ?? ''}
              onChange={(e) => handleEntryChange(e.target.value)}
              readOnly={Boolean(selectedArrow)}
            />
          </div>

          {/* Stop Loss (Price & Pips) */}
          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-sl">Stop Loss (Risk)</label>
              <div className="input-dual-labels">
                <span>Price</span>
                <span>Pips</span>
              </div>
            </div>
            <div className="dual-inputs-row">
              <input
                id="plan-sl"
                type="number"
                step="any"
                placeholder="SL Price"
                value={slPrice ?? ''}
                onChange={(e) => handleSlPriceChange(e.target.value)}
                readOnly={Boolean(selectedArrow)}
              />
              <div className="pips-input-wrapper">
                <input
                  type="number"
                  step="any"
                  placeholder="SL Pips"
                  value={calculatedMetrics.slPips != null ? calculatedMetrics.slPips.toFixed(1) : ''}
                  onChange={(e) => handleSlPipsChange(e.target.value)}
                  readOnly={Boolean(selectedArrow)}
                />
                <span className="pips-unit">p</span>
              </div>
            </div>
          </div>

          {/* Take Profit (Price & Pips) */}
          <div className="input-group">
            <div className="input-label-row">
              <label htmlFor="plan-tp">Take Profit (Target)</label>
              <div className="input-dual-labels">
                <span>Price</span>
                <span>Pips</span>
              </div>
            </div>
            <div className="dual-inputs-row">
              <input
                id="plan-tp"
                type="number"
                step="any"
                placeholder="TP Price"
                value={tpPrice ?? ''}
                onChange={(e) => handleTpPriceChange(e.target.value)}
                readOnly={Boolean(selectedArrow)}
              />
              <div className="pips-input-wrapper">
                <input
                  type="number"
                  step="any"
                  placeholder="TP Pips"
                  value={calculatedMetrics.tpPips != null ? calculatedMetrics.tpPips.toFixed(1) : ''}
                  onChange={(e) => handleTpPipsChange(e.target.value)}
                  readOnly={Boolean(selectedArrow)}
                />
                <span className="pips-unit">p</span>
              </div>
            </div>
          </div>

          {/* Target R:R Preset Buttons */}
          {!selectedArrow && (
            <div className="rr-presets-row">
              <span className="presets-label">Target R:R:</span>
              {[1.0, 1.25, 1.5, 2.0, 3.0].map((r) => (
                <button
                  key={r}
                  type="button"
                  className={`rr-preset-btn ${
                    calculatedMetrics.rrRatio != null && Math.abs(calculatedMetrics.rrRatio - r) < 0.05
                      ? 'active'
                      : ''
                  }`}
                  onClick={() => handleTargetRrChange(r)}
                  disabled={calculatedMetrics.slPips == null || calculatedMetrics.slPips <= 0}
                  title={`Set TP to ${r}x risk distance`}
                >
                  +{r}R
                </button>
              ))}
            </div>
          )}

          {/* Register Arrow CTA Button */}
          {!selectedArrow ? (
            <div className="register-action-wrap">
              <button
                type="button"
                className={`register-arrow-btn ${canRegister ? 'ready' : 'disabled'}`}
                onClick={handleRegisterClick}
                disabled={!canRegister}
              >
                ↗ Register Setup Arrow on Chart
              </button>
              {regSuccessMsg && <div className="reg-success-toast">{regSuccessMsg}</div>}
              {!canRegister && (
                <small className="register-hint">
                  Set Entry, Stop Loss, and Take Profit to pin this setup arrow to the chart.
                </small>
              )}
            </div>
          ) : (
            <div className="register-action-wrap">
              <div className="selected-arrow-actions">
                <button
                  type="button"
                  className="new-draft-btn"
                  onClick={() => onSelectArrowId(null)}
                >
                  + Create New Plan
                </button>
                <button
                  type="button"
                  className="delete-arrow-btn"
                  onClick={() => onDeleteArrow(selectedArrow.id)}
                >
                  Delete Arrow
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Col 2: Metric Calculations & Registered Setups List */}
      <div className="notebook-col notebook-metrics-col">
        <div className="notebook-col-header">
          <span className="notebook-eyebrow">Risk / Reward Math</span>
          <span className="source-tag">100% Deterministic</span>
        </div>

        {/* 3 Metric Cards */}
        <div className="metrics-cards-grid">
          <div className="metric-card">
            <span className="metric-lbl">Target Gain</span>
            <strong className="metric-val text-green">
              {calculatedMetrics.tpPips != null ? `+${calculatedMetrics.tpPips.toFixed(1)}p` : '—'}
            </strong>
            <small className="metric-sub">Distance to TP</small>
          </div>
          <div className="metric-card">
            <span className="metric-lbl">Max Risk</span>
            <strong className="metric-val text-rose">
              {calculatedMetrics.slPips != null ? `-${calculatedMetrics.slPips.toFixed(1)}p` : '—'}
            </strong>
            <small className="metric-sub">Distance to SL</small>
          </div>
          <div className="metric-card highlight">
            <span className="metric-lbl">Reward : Risk</span>
            <strong className="metric-val text-cyan">
              {calculatedMetrics.rrRatio != null ? `1 : ${calculatedMetrics.rrRatio.toFixed(2)}` : '—'}
            </strong>
            <small className="metric-sub">
              {calculatedMetrics.rrRatio != null ? `+${calculatedMetrics.rrRatio.toFixed(2)}R Multiplier` : 'Set TP & SL'}
            </small>
          </div>
        </div>

        {/* Registered Setups on this Pair */}
        <div className="registered-setups-section">
          <div className="setups-section-header">
            <strong>Registered Arrows ({registeredArrows.length})</strong>
            {selectedArrow && (
              <button type="button" className="clear-selection-link" onClick={() => onSelectArrowId(null)}>
                Deselect
              </button>
            )}
          </div>

          <div className="setups-chips-list">
            {registeredArrows.length === 0 ? (
              <div className="empty-arrows-notice">
                No arrows registered for {selectedSymbol} yet. Fill the execution plan on the left and click &quot;Register Setup Arrow&quot; to plot your first setup.
              </div>
            ) : (
              registeredArrows.map((arrow) => {
                const isSelected = arrow.id === selectedArrowId
                const isLong = arrow.direction === 'long'
                const dateStr = new Date(arrow.time * 1000).toLocaleDateString([], {
                  month: 'short',
                  day: 'numeric',
                })
                return (
                  <div
                    key={arrow.id}
                    className={`setup-chip ${isSelected ? 'selected' : ''}`}
                    onClick={() => onSelectArrowId(arrow.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => { if (e.key === 'Enter') onSelectArrowId(arrow.id) }}
                  >
                    <span className={`chip-dir ${isLong ? 'long' : 'short'}`}>
                      {isLong ? '↑ LONG' : '↓ SHORT'}
                    </span>
                    <span className="chip-date">{dateStr}</span>
                    <strong className="chip-rr">+{arrow.rrRatio.toFixed(2)}R</strong>
                    <span className="chip-levels">
                      TP {arrow.tpPips.toFixed(0)}p / SL {arrow.slPips.toFixed(0)}p
                    </span>
                    <button
                      type="button"
                      className="chip-delete-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteArrow(arrow.id)
                      }}
                      title="Delete this registered arrow"
                    >
                      ×
                    </button>
                  </div>
                )
              })
            )}
          </div>
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
          <span>Scope: <code className="font-mono">{selectedSymbol}</code></span>
          <span className="durability-hint">Durable across refresh</span>
        </footer>
      </div>
    </section>
  )
}
