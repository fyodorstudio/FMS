import type { ChartTimeframe } from '../contracts/ChartTimeframe'
import type { OhlcBar } from '../contracts/OhlcBar'
import type { SymbolQuote } from '../contracts/SymbolQuote'

const timeframeSeconds: Record<ChartTimeframe, number> = {
  M1: 60,
  M5: 300,
  M15: 900,
  M30: 1_800,
  H1: 3_600,
  H4: 14_400,
  D1: 86_400,
}

function hash(text: string) {
  let result = 2_166_136_261
  for (const character of text) {
    result ^= character.charCodeAt(0)
    result = Math.imul(result, 16_777_619)
  }
  return result >>> 0
}

function randomGenerator(seed: number) {
  let state = seed || 1
  return () => {
    state = Math.imul(1_664_525, state) + 1_013_904_223
    return (state >>> 0) / 4_294_967_296
  }
}

export function generateSampleBars(quote: SymbolQuote, timeframe: ChartTimeframe): OhlcBar[] {
  const random = randomGenerator(hash(`${quote.symbol}:${timeframe}`))
  const interval = timeframeSeconds[timeframe]
  const barCount = 260
  const endTime = Math.floor(Date.UTC(2026, 8, 21, 8, 0, 0) / 1000)
  const scale = quote.bid > 20 ? 0.0022 : 0.0014
  let close = quote.bid * (0.985 + random() * 0.02)

  return Array.from({ length: barCount }, (_, index) => {
    const open = close
    const move = (random() - 0.48) * quote.bid * scale
    close = Math.max(quote.bid * 0.7, open + move)
    const wick = quote.bid * scale * (0.18 + random() * 0.45)

    return {
      time: (endTime - (barCount - 1 - index) * interval) as OhlcBar['time'],
      open,
      high: Math.max(open, close) + wick * random(),
      low: Math.min(open, close) - wick * random(),
      close,
    }
  })
}
