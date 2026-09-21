import { useEffect } from 'react'
import {
  createSeriesMarkers,
  type IChartApi,
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
  onSelectArrow: (arrow: FmsChartArrow) => void
}

function markerColor(arrow: FmsChartArrow) {
  if (arrow.result === 'tp-reached') return '#078a67'
  if (arrow.result === 'sl-reached') return '#d34858'
  return '#64748b'
}

export function FmsChartMarkers({ chartApi, seriesApi, arrows, onSelectArrow }: FmsChartMarkersProps) {
  useEffect(() => {
    const markers: SeriesMarker<Time>[] = arrows.map((arrow) => ({
      id: arrow.id,
      time: arrow.time,
      price: arrow.price,
      position: arrow.direction === 'long' ? 'atPriceBottom' : 'atPriceTop',
      shape: arrow.direction === 'long' ? 'arrowUp' : 'arrowDown',
      color: markerColor(arrow),
      text: arrow.direction === 'long' ? 'LONG' : 'SHORT',
      size: 0.72,
    }))
    const markerApi = createSeriesMarkers(seriesApi, markers, { zOrder: 'top' })
    return () => markerApi.detach()
  }, [arrows, seriesApi])

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

  return null
}
