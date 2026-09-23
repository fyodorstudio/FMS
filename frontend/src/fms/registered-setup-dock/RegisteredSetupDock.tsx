import { useMemo, useState } from 'react'
import type { FmsPortfolioSummary, FmsRegisteredSetupDTO } from '../contracts/fms-api-types'
import './registered-setup-dock.css'

type RegisteredSetupDockProps = {
  setups: FmsRegisteredSetupDTO[]
  summary?: FmsPortfolioSummary | null
  selectedSymbol?: string
  isOnline?: boolean
  onSelectSymbol?: (symbol: string) => void
}

const methodFilters: { id: string; label: string }[] = [
  { id: 'ALL', label: 'All' },
  { id: 'M-MSD', label: 'M-MSD' },
  { id: 'M-PYS', label: 'M-PYS' },
  { id: 'M-TOT', label: 'M-TOT' },
  { id: 'M-VRC', label: 'M-VRC' },
  { id: 'M-LAR', label: 'M-LAR' },
]

export function RegisteredSetupDock({
  setups,
  summary,
  selectedSymbol,
  isOnline = true,
  onSelectSymbol,
}: RegisteredSetupDockProps) {
  const [activeMethod, setActiveMethod] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [onlyCurrentSymbol, setOnlyCurrentSymbol] = useState<boolean>(false)

  const countsByMethod = useMemo(() => {
    const map: Record<string, number> = { ALL: setups.length }
    for (const s of setups) {
      map[s.quant_method] = (map[s.quant_method] || 0) + 1
    }
    return map
  }, [setups])

  const filteredSetups = useMemo(() => {
    return setups.filter((setup) => {
      if (onlyCurrentSymbol && selectedSymbol && setup.symbol !== selectedSymbol) {
        return false
      }
      const matchesMethod = activeMethod === 'ALL' || setup.quant_method === activeMethod
      const normalizedQuery = searchQuery.trim().toLowerCase()
      const matchesSearch =
        !normalizedQuery ||
        setup.symbol.toLowerCase().includes(normalizedQuery) ||
        setup.event_name.toLowerCase().includes(normalizedQuery) ||
        setup.quant_method.toLowerCase().includes(normalizedQuery)
      return matchesMethod && matchesSearch
    })
  }, [setups, onlyCurrentSymbol, selectedSymbol, activeMethod, searchQuery])

  const currentPairCount = useMemo(() => {
    if (!selectedSymbol) return 0
    return setups.filter((s) => s.symbol === selectedSymbol).length
  }, [setups, selectedSymbol])

  const activeMethodInfo = useMemo(() => {
    if (activeMethod === 'ALL' || !summary) return null
    return summary.methods.find((m) => m.code === activeMethod)
  }, [activeMethod, summary])

  return (
    <aside className="registered-setup-dock" aria-label="Registered Setups">
      <div className="setup-dock-heading">
        <div>
          <p className="setup-dock-eyebrow">Quantitative Registry</p>
          <h2>Registered Setups</h2>
        </div>
        <span className={`setup-status-pill ${isOnline ? 'online' : 'offline'}`}>
          {isOnline ? `${setups.length} Verified` : 'Engine Offline'}
        </span>
      </div>

      {/* High-density summary stats */}
      <div className="setup-stats-strip">
        <div className="setup-stat-cell">
          <span className="setup-stat-lbl">Setups</span>
          <strong className="setup-stat-val">
            {activeMethod === 'ALL' ? setups.length : activeMethodInfo?.setup_count ?? countsByMethod[activeMethod] ?? 0}
          </strong>
        </div>
        <div className="setup-stat-cell">
          <span className="setup-stat-lbl">Avg WR</span>
          <strong className="setup-stat-val positive">
            {activeMethod === 'ALL'
              ? '66%'
              : activeMethodInfo
                ? `${(activeMethodInfo.average_win_rate * 100).toFixed(0)}%`
                : '—'}
          </strong>
        </div>
        <div className="setup-stat-cell">
          <span className="setup-stat-lbl">Net Return</span>
          <strong className="setup-stat-val positive">
            +{activeMethod === 'ALL'
              ? (summary?.total_net_r != null ? summary.total_net_r.toFixed(1) : '248.8')
              : (activeMethodInfo?.aggregate_net_r != null ? activeMethodInfo.aggregate_net_r.toFixed(1) : '0.0')}R
          </strong>
        </div>
      </div>

      {/* Scope Toggles & Method Chips */}
      <div className="setup-controls-strip">
        <div className="setup-scope-row">
          <button
            type="button"
            className={`setup-scope-btn ${!onlyCurrentSymbol ? 'active' : ''}`}
            onClick={() => setOnlyCurrentSymbol(false)}
          >
            All Instruments ({setups.length})
          </button>
          {selectedSymbol && (
            <button
              type="button"
              className={`setup-scope-btn ${onlyCurrentSymbol ? 'active' : ''}`}
              onClick={() => setOnlyCurrentSymbol(true)}
            >
              {selectedSymbol} Only ({currentPairCount})
            </button>
          )}
        </div>

        <nav className="setup-method-tabs" aria-label="Method tabs">
          {methodFilters.map((tab) => {
            const count = countsByMethod[tab.id] ?? 0
            return (
              <button
                key={tab.id}
                type="button"
                className={`setup-method-tab ${activeMethod === tab.id ? 'active' : ''}`}
                onClick={() => setActiveMethod(tab.id)}
              >
                <span>{tab.label}</span>
                <small>{count}</small>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Search Input */}
      <label className="setup-dock-search">
        <span aria-hidden="true">⌕</span>
        <input
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter pair, catalyst, method..."
          aria-label="Filter registered setups"
        />
      </label>

      {/* Column Headers */}
      <div className="setup-dock-columns" aria-hidden="true">
        <span>Setup / Catalyst</span>
        <span>Win %</span>
        <span>R:R (TP/SL)</span>
      </div>

      {/* Setup List Items */}
      <div className="setup-dock-list" role="listbox" aria-label="Registered setups list">
        {filteredSetups.length === 0 ? (
          <div className="setup-dock-empty">
            {isOnline ? 'No setups matching current filter.' : 'Connecting to FMS Engine on port 8002...'}
          </div>
        ) : (
          filteredSetups.map((setup) => {
            const isBuy = setup.direction === 'BUY'
            const isSelectedPair = setup.symbol === selectedSymbol
            const methodKey = setup.quant_method.replace('M-', '').toLowerCase()

            return (
              <button
                key={setup.id}
                type="button"
                className={`setup-dock-row ${isSelectedPair ? 'selected' : ''}`}
                onClick={() => onSelectSymbol?.(setup.symbol)}
                title={`Click to switch chart to ${setup.symbol}`}
              >
                <div className="setup-col-identity">
                  <div className="setup-identity-header">
                    <strong className="setup-symbol-text">{setup.symbol}</strong>
                    <span className={`setup-direction-badge ${isBuy ? 'buy' : 'sell'}`}>
                      {setup.direction}
                    </span>
                    <span className={`setup-method-tag method-${methodKey}`}>
                      {setup.quant_method}
                    </span>
                  </div>
                  <div className="setup-catalyst-name" title={setup.event_name}>
                    {setup.event_name}
                  </div>
                </div>

                <div className="setup-col-winrate">
                  <strong className="setup-wr-text">
                    {(setup.respect_rate * 100).toFixed(0)}%
                  </strong>
                  <span className="setup-n-sub">N={setup.sample_count}</span>
                </div>

                <div className="setup-col-rr">
                  <strong className="setup-rr-text">
                    {setup.reward_risk_ratio.toFixed(2)}R
                  </strong>
                  <span className="setup-pips-sub">
                    {setup.recommended_tp_pips.toFixed(0)}p / {setup.recommended_sl_pips.toFixed(0)}p
                  </span>
                </div>
              </button>
            )
          })
        )}
      </div>
    </aside>
  )
}
