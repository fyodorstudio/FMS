import type { ChartTimeframe } from '../contracts/ChartTimeframe'
import type { ChartDrawingPoint } from './chart-drawing-record'
import type { DrawingToolId } from './drawing-tool'

export function timeframeToSeconds(timeframe?: ChartTimeframe): number {
  switch (timeframe) {
    case 'M1': return 60
    case 'M5': return 300
    case 'M15': return 900
    case 'M30': return 1800
    case 'H1': return 3600
    case 'H4': return 14400
    case 'D1': return 86400
    default: return 14400
  }
}

export function timeframeToPricePercent(timeframe?: ChartTimeframe): number {
  switch (timeframe) {
    case 'M1': return 0.0015
    case 'M5': return 0.0025
    case 'M15': return 0.0040
    case 'M30': return 0.0055
    case 'H1': return 0.0075
    case 'H4': return 0.0100
    case 'D1': return 0.0180
    default: return 0.0075
  }
}

export function normalizeDrawingPoints(
  tool: DrawingToolId,
  points: ChartDrawingPoint[],
  timeframe?: ChartTimeframe,
) {
  if ((tool !== 'long-position' && tool !== 'short-position') || points.length < 2) return points

  const entry = points[0]
  const dragged = points.at(-1)!
  const long = tool === 'long-position'

  const defaultSpanSec = timeframeToSeconds(timeframe) * 15
  const isSingleClick = Math.abs(dragged.time - entry.time) < 60
  const time = isSingleClick
    ? ((entry.time + defaultSpanSec) as ChartDrawingPoint['time'])
    : dragged.time

  const defaultDistance = Math.max(Math.abs(entry.price) * timeframeToPricePercent(timeframe), 0.0010)
  const distance = isSingleClick
    ? defaultDistance
    : Math.max(Math.abs(dragged.price - entry.price), Math.abs(entry.price) * 0.0005 || 0.0005)

  return [
    entry,
    { time, price: entry.price + (long ? distance : -distance) },
    { time, price: entry.price + (long ? -distance : distance) },
  ]
}
