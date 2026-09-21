import { useMemo, useState } from 'react'
import type { SymbolQuote } from '../contracts/SymbolQuote'
import './market-watch-panel.css'

type MarketWatchPanelProps = {
  symbols: SymbolQuote[]
  selectedSymbol: string
  onSelect: (symbol: string) => void
}

function formatPrice(value: number, precision: number) {
  return value.toFixed(precision)
}

export function MarketWatchPanel({ symbols, selectedSymbol, onSelect }: MarketWatchPanelProps) {
  const [query, setQuery] = useState('')
  const filteredSymbols = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    if (!normalized) return symbols
    return symbols.filter(
      (quote) =>
        quote.symbol.toLowerCase().includes(normalized) ||
        quote.description.toLowerCase().includes(normalized),
    )
  }, [query, symbols])

  return (
    <aside className="market-watch" aria-label="Market Watch">
      <div className="market-watch-heading">
        <div>
          <p className="market-watch-eyebrow">Instruments</p>
          <h2>Market Watch</h2>
        </div>
        <span className="market-watch-count">{symbols.length}</span>
      </div>

      <label className="market-watch-search">
        <span aria-hidden="true">⌕</span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search symbols"
          aria-label="Search symbols"
        />
      </label>

      <div className="market-watch-columns" aria-hidden="true">
        <span>Symbol</span>
        <span>Bid</span>
        <span>Ask</span>
      </div>

      <div className="market-watch-list" role="listbox" aria-label="Available symbols">
        {filteredSymbols.map((quote) => {
          const selected = quote.symbol === selectedSymbol
          const positive = quote.dailyChange >= 0

          return (
            <button
              className={`market-watch-row${selected ? ' selected' : ''}`}
              key={quote.symbol}
              type="button"
              role="option"
              aria-selected={selected}
              onClick={() => onSelect(quote.symbol)}
            >
              <span className="market-watch-identity">
                <strong>{quote.symbol}</strong>
                <small className={positive ? 'positive' : 'negative'}>
                  {positive ? '+' : ''}{quote.dailyChange.toFixed(2)}%
                </small>
              </span>
              <span>{formatPrice(quote.bid, quote.precision)}</span>
              <span>{formatPrice(quote.ask, quote.precision)}</span>
            </button>
          )
        })}

        {filteredSymbols.length === 0 && <p className="market-watch-empty">No matching symbol</p>}
      </div>
    </aside>
  )
}
