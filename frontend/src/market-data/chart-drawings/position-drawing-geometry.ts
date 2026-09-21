import type { ChartDrawingPoint } from './chart-drawing-record'
import type { DrawingToolId } from './drawing-tool'

export function normalizeDrawingPoints(tool: DrawingToolId, points: ChartDrawingPoint[]) {
  if ((tool !== 'long-position' && tool !== 'short-position') || points.length < 2) return points

  const entry = points[0]
  const dragged = points.at(-1)!
  const distance = Math.max(Math.abs(dragged.price - entry.price), Math.abs(entry.price) * 0.001)
  const long = tool === 'long-position'

  return [
    entry,
    { time: dragged.time, price: entry.price + (long ? distance : -distance) },
    { time: dragged.time, price: entry.price + (long ? -distance : distance) },
  ]
}
