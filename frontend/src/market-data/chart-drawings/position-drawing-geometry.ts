import type { ChartDrawingPoint } from './chart-drawing-record'
import type { DrawingToolId } from './drawing-tool'

export function normalizeDrawingPoints(tool: DrawingToolId, points: ChartDrawingPoint[]) {
  if ((tool !== 'long-position' && tool !== 'short-position') || points.length < 2) return points

  const entry = points[0]
  const dragged = points.at(-1)!
  const long = tool === 'long-position'

  const defaultSpanSec = 15 * 3600
  const time = Math.abs(dragged.time - entry.time) < 60
    ? ((entry.time + defaultSpanSec) as ChartDrawingPoint['time'])
    : dragged.time

  const minDelta = Math.abs(entry.price) * 0.0035 || 0.0035
  const distance = Math.max(Math.abs(dragged.price - entry.price), minDelta)

  return [
    entry,
    { time, price: entry.price + (long ? distance : -distance) },
    { time, price: entry.price + (long ? -distance : distance) },
  ]
}
