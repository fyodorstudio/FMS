import { useEffect } from 'react'
import {
  LineStyle,
  type IPriceLine,
  type ISeriesApi,
  type Time,
} from 'lightweight-charts'

type PlannedTradePriceLinesProps = {
  seriesApi: ISeriesApi<'Candlestick', Time>
  visible: boolean
  direction: 'long' | 'short'
  entryPrice?: number | null
  tpPrice?: number | null
  slPrice?: number | null
}

export function PlannedTradePriceLines({
  seriesApi,
  visible,
  direction,
  entryPrice,
  tpPrice,
  slPrice,
}: PlannedTradePriceLinesProps) {
  useEffect(() => {
    if (!visible) return

    const lines: IPriceLine[] = []

    // 1. Entry Line
    if (entryPrice != null && !Number.isNaN(entryPrice) && entryPrice > 0) {
      lines.push(
        seriesApi.createPriceLine({
          price: entryPrice,
          color: '#0284c7',
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          lineVisible: true,
          axisLabelVisible: true,
          title: `ENTRY (${direction.toUpperCase()}): ${entryPrice.toFixed(5)}`,
        }),
      )
    }

    // 2. Take Profit Line
    if (tpPrice != null && !Number.isNaN(tpPrice) && tpPrice > 0) {
      lines.push(
        seriesApi.createPriceLine({
          price: tpPrice,
          color: '#10b981',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          lineVisible: true,
          axisLabelVisible: true,
          title: `TP: ${tpPrice.toFixed(5)}`,
        }),
      )
    }

    // 3. Stop Loss Line
    if (slPrice != null && !Number.isNaN(slPrice) && slPrice > 0) {
      lines.push(
        seriesApi.createPriceLine({
          price: slPrice,
          color: '#e11d48',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          lineVisible: true,
          axisLabelVisible: true,
          title: `SL: ${slPrice.toFixed(5)}`,
        }),
      )
    }

    return () => {
      for (const line of lines) {
        try {
          seriesApi.removePriceLine(line)
        } catch {
          // ignore cleanup errors
        }
      }
    }
  }, [direction, entryPrice, seriesApi, slPrice, tpPrice, visible])

  return null
}
