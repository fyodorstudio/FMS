import type { UTCTimestamp } from 'lightweight-charts'
import type { ChartTimeframe } from '../../market-data/contracts/ChartTimeframe'

export type FmsDecisionState = 'upcoming' | 'current' | 'recent'
export type FmsDecisionResult = 'tp-reached' | 'sl-reached' | 'no-trade' | 'open'
export type FmsArrowFilter = 'all' | 'wins' | 'losses' | 'buys' | 'sells' | string

export type FmsDecision = {
  id: string
  symbol: string
  setupName: string
  eventName: string
  releaseTime: number
  state: FmsDecisionState
  direction: 'long' | 'short'
  result: FmsDecisionResult
  resultR: number | null
  version: 'v1' | 'v2'
  method?: string
  price?: number
  entryPrice?: number
  tpPrice?: number
  slPrice?: number
  recommendedTpPips?: number
  recommendedSlPips?: number
  mfePips?: number
  maePips?: number
  reason?: string
}

export type FmsChartArrow = {
  id: string
  symbol: string
  timeframe: ChartTimeframe
  time: UTCTimestamp
  price: number
  direction: 'long' | 'short'
  result: FmsDecisionResult
  resultR: number | null
  version: 'v1' | 'v2'
  setupName: string
  eventName: string
  releaseTime: number
  method?: string
  entryPrice?: number
  tpPrice?: number
  slPrice?: number
  recommendedTpPips?: number
  recommendedSlPips?: number
  mfePips?: number
  maePips?: number
  reason?: string
}

export type FmsRegisteredSetup = {
  id: string
  version: 'v1' | 'v2'
  name: string
  pairFamily: string
  entryRule: string
  status: 'Frozen example' | 'Research example'
}
