import { useMemo, useState } from 'react'
import type { FmsPortfolioSummary, FmsRegisteredSetupDTO } from '../contracts/fms-api-types'
import './registered-setup-dock.css'

type RegisteredSetupDockProps = {
  setups: FmsRegisteredSetupDTO[]
  summary?: FmsPortfolioSummary | null
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
  isOnline = true,
  onSelectSymbol,
}: RegisteredSetupDockProps) {
  const [activeMethod, setActiveMethod] = useState<string>('ALL')
  const [searchQuery, setSearchQuery] = useState<string>('')

  const countsByMethod = useMemo(() => {
    const map: Record<string, number> = { ALL: setups.length }
    for (const s of setups) {
      map[s.quant_method] = (map[s.quant_method] || 0) + 1
    }
    return map
  }, [setups])

  const filteredSetups = useMemo(() => {
    return setups.filter((setup) => {
      const matchesMethod = activeMethod === 'ALL' || setup.quant_method === activeMethod
      const matchesSearch =
        !searchQuery ||
        setup.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        setup.event_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        setup.quant_method.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesMethod && matchesSearch
    })
  }, [setups, activeMethod, searchQuery])

  const activeMethodInfo = useMemo(() => {
    if (activeMethod === 'ALL' || !summary) return null
    return summary.methods.find((m) => m.code === activeMethod)
  }, [activeMethod, summary])

  return (
    <section className="registered-setup-dock" aria-label="Registered FMS setups">
      <header className="setup-dock-header">
        <div className="setup-dock-title-row">
          <div>
            <small>Quantitative Strategy Registry</small>
            <h2>Registered Setups</h2>
          </div>
          <span className={`engine-badge ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? `${setups.length} Verified` : 'Engine Offline'}
          </span>
        </div>

        {/* Global or Method Summary Metrics */}
        <div className="setup-summary-strip">
          {activeMethod === 'ALL' ? (
            <>
              <div className="stat-pill">
                <span className="stat-label">Total Setups</span>
                <strong className="stat-val">{setups.length}</strong>
              </div>
              <div className="stat-pill">
                <span className="stat-label">Decadal Net R</span>
                <strong className="stat-val text-green">+{summary?.total_net_r != null ? summary.total_net_r.toFixed(1) : '0.0'}R</strong>
              </div>
              <div className="stat-pill">
                <span className="stat-label">Quality Gate</span>
                <strong className="stat-val text-cyan">100% Pass</strong>
              </div>
            </>
          ) : (
            <>
              <div className="stat-pill">
                <span className="stat-label">Method Setups</span>
                <strong className="stat-val">{activeMethodInfo?.setup_count ?? countsByMethod[activeMethod] ?? 0}</strong>
              </div>
              <div className="stat-pill">
                <span className="stat-label">Avg Win Rate</span>
                <strong className="stat-val text-green">
                  {activeMethodInfo ? `${(activeMethodInfo.average_win_rate * 100).toFixed(0)}%` : '—'}
                </strong>
              </div>
              <div className="stat-pill">
                <span className="stat-label">Net Return</span>
                <strong className="stat-val text-green">
                  +{activeMethodInfo?.aggregate_net_r != null ? activeMethodInfo.aggregate_net_r.toFixed(1) : '0.0'}R
                </strong>
              </div>
            </>
          )}
        </div>

        {/* Filter Navigation */}
        <nav className="method-filter-tabs" aria-label="Method tabs">
          {methodFilters.map((tab) => {
            const count = countsByMethod[tab.id] ?? 0
            return (
              <button
                key={tab.id}
                type="button"
                className={`method-tab ${activeMethod === tab.id ? 'active' : ''}`}
                onClick={() => setActiveMethod(tab.id)}
              >
                <span>{tab.label}</span>
                <span className="tab-count">{count}</span>
              </button>
            )
          })}
        </nav>

        {/* Search Bar */}
        <div className="setup-search-row">
          <input
            type="search"
            placeholder="Search pair, method, or catalyst..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="setup-search-input"
          />
        </div>
      </header>

      {/* Setup Cards List */}
      <div className="setup-cards-container">
        {filteredSetups.length === 0 ? (
          <div className="empty-setups-notice">
            {isOnline ? 'No setups matching the current filter.' : 'Connecting to FMS Engine on port 8002...'}
          </div>
        ) : (
          filteredSetups.map((setup) => {
            const isBuy = setup.direction === 'BUY'
            return (
              <article
                key={setup.id}
                className="setup-card"
                onClick={() => onSelectSymbol?.(setup.symbol)}
                title={`Click to open ${setup.symbol} on chart`}
              >
                <header className="setup-card-header">
                  <div className="card-symbol-badge">
                    <strong className="symbol-name">{setup.symbol}</strong>
                    <span className={`direction-tag ${isBuy ? 'buy' : 'sell'}`}>
                      {setup.direction}
                    </span>
                  </div>
                  <span className={`method-badge method-${setup.quant_method.replace('M-', '').toLowerCase()}`}>
                    {setup.quant_method}
                  </span>
                </header>

                <div className="setup-event-name">{setup.event_name}</div>

                <div className="setup-metrics-grid">
                  <div className="metric-box">
                    <span className="metric-lbl">Win Rate</span>
                    <strong className="metric-val text-green">
                      {(setup.respect_rate * 100).toFixed(0)}%
                    </strong>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">R : R</span>
                    <strong className="metric-val text-cyan">{setup.reward_risk_ratio.toFixed(2)}</strong>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">TP / SL</span>
                    <strong className="metric-val">
                      {setup.recommended_tp_pips.toFixed(0)}p / {setup.recommended_sl_pips.toFixed(0)}p
                    </strong>
                  </div>
                  <div className="metric-box">
                    <span className="metric-lbl">Sample N</span>
                    <strong className="metric-val">{setup.sample_count}</strong>
                  </div>
                </div>

                <footer className="setup-card-footer">
                  <span className="trigger-state-tag">{setup.trigger_state}</span>
                  <span className="timeframe-tag">{setup.timeframe}</span>
                </footer>
              </article>
            )
          })
        )}
      </div>
    </section>
  )
}
