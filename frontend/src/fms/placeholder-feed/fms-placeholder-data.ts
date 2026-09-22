import type { OhlcBar } from '../../market-data/contracts/OhlcBar'
import type { ChartTimeframe } from '../../market-data/contracts/ChartTimeframe'
import type { FmsChartArrow, FmsDecision, FmsRegisteredSetup } from './fms-placeholder-types'

/**
 * ANTI-HALLUCINATION COVENANT:
 * Zero synthetic or modulo data allowed.
 * All decisions, arrows, and registered setups must come directly from verified broker feeds and the FMS API.
 */
export const fmsPlaceholderDecisions: FmsDecision[] = []
export const fmsPlaceholderSetups: FmsRegisteredSetup[] = []

export function createFmsPlaceholderArrows(
  _symbol: string,
  _timeframe: ChartTimeframe,
  _bars: OhlcBar[],
): FmsChartArrow[] {
  return []
}
