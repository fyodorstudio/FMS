import { useEffect, useRef, useState } from 'react'
import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import type { FmsChartArrow } from '../placeholder-feed/fms-placeholder-types'
import './fms-chart-arrow-overlay.css'

type FmsChartArrowOverlayProps = {
  chartApi: IChartApi
  seriesApi: ISeriesApi<'Candlestick', Time>
  arrows: FmsChartArrow[]
  onSelectArrow: (arrow: FmsChartArrow) => void
}

export function FmsChartArrowOverlay({ chartApi, seriesApi, arrows, onSelectArrow }: FmsChartArrowOverlayProps) {
  const overlayRef = useRef<HTMLDivElement>(null)
  const [, setRevision] = useState(0)

  useEffect(() => {
    const overlay = overlayRef.current
    if (!overlay) return
    const refresh = () => setRevision((revision) => revision + 1)
    const resizeObserver = new ResizeObserver(refresh)
    resizeObserver.observe(overlay)
    chartApi.timeScale().subscribeVisibleLogicalRangeChange(refresh)
    refresh()
    return () => {
      resizeObserver.disconnect()
      chartApi.timeScale().unsubscribeVisibleLogicalRangeChange(refresh)
    }
  }, [chartApi])

  return (
    <div ref={overlayRef} className="fms-chart-arrow-overlay" aria-label="FMS historical arrows">
      {arrows.map((arrow) => {
        const x = chartApi.timeScale().timeToCoordinate(arrow.time)
        const y = seriesApi.priceToCoordinate(arrow.price)
        if (x === null || y === null) return null
        return (
          <button
            key={arrow.id}
            type="button"
            className={`fms-chart-arrow ${arrow.direction} ${arrow.result}`}
            style={{ transform: `translate(${x}px, ${y}px)` }}
            onClick={() => onSelectArrow(arrow)}
            title={`${arrow.symbol} · ${arrow.setupName} · open Past Result`}
          >
            <span aria-hidden="true" />
            <strong>{arrow.direction === 'long' ? 'LONG' : 'SHORT'}</strong>
          </button>
        )
      })}
    </div>
  )
}
