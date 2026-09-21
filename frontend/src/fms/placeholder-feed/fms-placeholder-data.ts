import type { OhlcBar } from '../../market-data/contracts/OhlcBar'
import type { ChartTimeframe } from '../../market-data/contracts/ChartTimeframe'
import type { FmsChartArrow, FmsDecision, FmsRegisteredSetup } from './fms-placeholder-types'

const eventNames = [
  'Consumer sentiment',
  'Composite PMI',
  'Industrial production',
  'Payroll release',
  'Retail sales',
  'Business confidence',
]

const setupNames = [
  'Event follow-through',
  'Release rejection',
  'Directional surprise',
  'Post-release continuation',
]

const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD']

export const fmsPlaceholderDecisions: FmsDecision[] = symbols.flatMap((symbol, symbolIndex) => [
  {
    id: `${symbol}-upcoming`,
    symbol,
    setupName: setupNames[symbolIndex % setupNames.length],
    eventName: eventNames[symbolIndex % eventNames.length],
    releaseTime: Date.UTC(2026, 8, 23 + symbolIndex, 8 + symbolIndex, 30),
    state: 'upcoming' as const,
    direction: symbolIndex % 2 === 0 ? 'long' as const : 'short' as const,
    result: 'open' as const,
    resultR: null,
    version: symbolIndex < 3 ? 'v2' as const : 'v1' as const,
  },
  {
    id: `${symbol}-recent`,
    symbol,
    setupName: setupNames[(symbolIndex + 1) % setupNames.length],
    eventName: eventNames[(symbolIndex + 2) % eventNames.length],
    releaseTime: Date.UTC(2026, 8, 10 + symbolIndex, 10 + symbolIndex),
    state: 'recent' as const,
    direction: symbolIndex % 2 === 0 ? 'short' as const : 'long' as const,
    result: symbolIndex % 3 === 0 ? 'tp-reached' as const : symbolIndex % 3 === 1 ? 'sl-reached' as const : 'no-trade' as const,
    resultR: symbolIndex % 3 === 0 ? 2.5 : symbolIndex % 3 === 1 ? -1 : null,
    version: symbolIndex % 2 === 0 ? 'v1' as const : 'v2' as const,
  },
])

fmsPlaceholderDecisions.splice(2, 0, {
  id: 'EURUSD-current',
  symbol: 'EURUSD',
  setupName: 'Post-release continuation',
  eventName: 'Manufacturing employment',
  releaseTime: Date.UTC(2026, 8, 21, 8),
  state: 'current',
  direction: 'long',
  result: 'open',
  resultR: null,
  version: 'v2',
})

export const fmsPlaceholderSetups: FmsRegisteredSetup[] = [
  { id: 'setup-v1-follow', version: 'v1', name: 'Release follow-through', pairFamily: 'USD majors', entryRule: 'H4 entry after release', status: 'Frozen example' },
  { id: 'setup-v1-reject', version: 'v1', name: 'Event rejection', pairFamily: 'EUR crosses', entryRule: 'H4 rejection confirmation', status: 'Frozen example' },
  { id: 'setup-v2-successor', version: 'v2', name: 'Event-specific successor', pairFamily: 'Selected pair/event', entryRule: 'Separate entry, TP and expiry', status: 'Research example' },
]

export function createFmsPlaceholderArrows(
  symbol: string,
  timeframe: ChartTimeframe,
  bars: OhlcBar[],
): FmsChartArrow[] {
  if (bars.length < 180) return []
  const indices = [62, 105, 148, 192, 225]
  return indices.map((index, arrowIndex) => {
    const bar = bars[index]
    const direction = arrowIndex % 2 === 0 ? 'long' as const : 'short' as const
    const result = arrowIndex % 3 === 0 ? 'tp-reached' as const : arrowIndex % 3 === 1 ? 'sl-reached' as const : 'no-trade' as const
    const priceOffset = Math.max((bar.high - bar.low) * 0.75, bar.close * 0.0005)
    return {
      id: `${symbol}-${timeframe}-arrow-${arrowIndex}`,
      symbol,
      timeframe,
      time: bar.time,
      price: direction === 'long' ? bar.low - priceOffset : bar.high + priceOffset,
      direction,
      result,
      resultR: result === 'tp-reached' ? 1.5 + arrowIndex * 0.35 : result === 'sl-reached' ? -1 : null,
      version: arrowIndex < 3 ? 'v1' : 'v2',
      setupName: setupNames[arrowIndex % setupNames.length],
      eventName: eventNames[(arrowIndex + 1) % eventNames.length],
      releaseTime: Number(bar.time) * 1000,
    }
  })
}
