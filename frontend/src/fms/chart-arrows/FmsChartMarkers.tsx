import { useEffect } from 'react'
import {
  createSeriesMarkers,
  LineStyle,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
  type MouseEventParams,
  type SeriesMarker,
  type Time,
} from 'lightweight-charts'
import type { FmsChartArrow } from '../placeholder-feed/fms-placeholder-types'

type FmsChartMarkersProps = {
  chartApi: IChartApi
  seriesApi: ISeriesApi<'Candlestick', Time>
  arrows: FmsChartArrow[]
  selectedArrowId?: string | null
  onSelectArrow: (arrow: FmsChartArrow) => void
}

function markerColor(arrow: FmsChartArrow, isSelected: boolean) {
  if (isSelected) return '#38bdf8'
  if (arrow.result === 'tp-reached') return '#078a67'
  if (arrow.result === 'sl-reached') return '#d34858'
  return '#64748b'
}

export function FmsChartMarkers({
  chartApi,
  seriesApi,
  arrows,
  selectedArrowId,
  onSelectArrow,
}: FmsChartMarkersProps) {
  // 1. Draw markers for all visible arrows on this pair
  useEffect(() => {
    const markers: SeriesMarker<Time>[] = arrows.map((arrow) => {
      const isSelected = selectedArrowId === arrow.id
      return {
        id: arrow.id,
        time: arrow.time,
        price: arrow.price,
        position: arrow.direction === 'long' ? 'atPriceBottom' : 'atPriceTop',
        shape: arrow.direction === 'long' ? 'arrowUp' : 'arrowDown',
        color: markerColor(arrow, isSelected),
        text: isSelected
          ? `★ ${arrow.direction.toUpperCase()}`
          : arrow.direction === 'long'
            ? 'LONG'
            : 'SHORT',
        size: isSelected ? 1.15 : 0.72,
      }
    })
    const markerApi = createSeriesMarkers(seriesApi, markers, { zOrder: 'top' })
    return () => markerApi.detach()
  }, [arrows, selectedArrowId, seriesApi])

  // 2. Handle marker click to select arrow
  useEffect(() => {
    const handleClick = (event: MouseEventParams<Time>) => {
      const objectId = event.hoveredInfo?.objectId ?? event.hoveredObjectId
      if (typeof objectId !== 'string') return
      const arrow = arrows.find((candidate) => candidate.id === objectId)
      if (arrow) onSelectArrow(arrow)
    }
    chartApi.subscribeClick(handleClick)
    return () => chartApi.unsubscribeClick(handleClick)
  }, [arrows, chartApi, onSelectArrow])

  // 3. Draw horizontal TP, SL, and Entry price lines when an arrow is selected
  useEffect(() => {
    if (!selectedArrowId) return
    const arrow = arrows.find((a) => a.id === selectedArrowId)
    if (!arrow) return

    const lines: IPriceLine[] = []

    // A. Entry Price Line
    const entryPrice = arrow.entryPrice ?? arrow.price
    if (entryPrice != null && !Number.isNaN(entryPrice)) {
      lines.push(
        seriesApi.createPriceLine({
          price: entryPrice,
          color: '#0284c7',
          lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          lineVisible: true,
          axisLabelVisible: true,
          title: `ENTRY (${arrow.direction.toUpperCase()}): ${entryPrice.toFixed(5)}`,
        }),
      )
    }

    // B. Take Profit Line
    if (arrow.tpPrice != null && !Number.isNaN(arrow.tpPrice)) {
      lines.push(
        seriesApi.createPriceLine({
          price: arrow.tpPrice,
          color: '#10b981',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          lineVisible: true,
          axisLabelVisible: true,
          title: `TP (+1.25R): ${arrow.tpPrice.toFixed(5)}`,
        }),
      )
    }

    // C. Stop Loss Line
    if (arrow.slPrice != null && !Number.isNaN(arrow.slPrice)) {
      lines.push(
        seriesApi.createPriceLine({
          price: arrow.slPrice,
          color: '#e11d48',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          lineVisible: true,
          axisLabelVisible: true,
          title: `SL (-1.00R): ${arrow.slPrice.toFixed(5)}`,
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
  }, [arrows, selectedArrowId, seriesApi])

  return null
}
