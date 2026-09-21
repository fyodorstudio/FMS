import type { ChartTimeframe } from '../market-data/contracts/ChartTimeframe'
import type { SymbolQuote } from '../market-data/contracts/SymbolQuote'

const timeframes: ChartTimeframe[] = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']

type ChartWorkspaceHeaderProps = {
  quote: SymbolQuote
  timeframe: ChartTimeframe
  onSelectTimeframe: (timeframe: ChartTimeframe) => void
}

export function ChartWorkspaceHeader({ quote, timeframe, onSelectTimeframe }: ChartWorkspaceHeaderProps) {
  return (
    <div className="chart-toolbar">
      <div className="active-market">
        <div className="market-icon">{quote.symbol.slice(0, 2)}</div>
        <div>
          <div className="market-title-row">
            <h1>{quote.symbol}</h1>
            <span className={quote.dailyChange >= 0 ? 'positive' : 'negative'}>
              {quote.dailyChange >= 0 ? '+' : ''}{quote.dailyChange.toFixed(2)}%
            </span>
          </div>
          <p>{quote.description}</p>
        </div>
      </div>

      <div className="timeframe-selector" aria-label="Chart timeframe">
        {timeframes.map((item) => (
          <button
            key={item}
            type="button"
            className={item === timeframe ? 'active' : ''}
            aria-pressed={item === timeframe}
            onClick={() => onSelectTimeframe(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="quote-summary">
        <span><small>Bid</small>{quote.bid.toFixed(quote.precision)}</span>
        <span><small>Ask</small>{quote.ask.toFixed(quote.precision)}</span>
      </div>
    </div>
  )
}
