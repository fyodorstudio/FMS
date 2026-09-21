import type { UTCTimestamp } from 'lightweight-charts'
import type { ChartTimeframe } from '../contracts/ChartTimeframe'
import type { DrawingToolId } from './drawing-tool'

export type ChartDrawingPoint = {
  time: UTCTimestamp
  price: number
}

export type ChartDrawingRecord = {
  id: string
  symbol: string
  timeframe: ChartTimeframe
  tool: DrawingToolId
  points: ChartDrawingPoint[]
  createdAt: number
}
