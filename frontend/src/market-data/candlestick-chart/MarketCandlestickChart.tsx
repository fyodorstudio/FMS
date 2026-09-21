import { useEffect, useRef, useState, type ReactNode } from 'react'
import {
  CandlestickSeries,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from 'lightweight-charts'
import type { ColorTheme } from '../../appearance/color-theme/color-theme-preference'
import type { TimeDisplayPreference } from '../../appearance/time-display/time-display-preference'
import { ChartDrawingOverlay } from '../chart-drawings/ChartDrawingOverlay'
import type { ChartDrawingPoint, ChartDrawingRecord } from '../chart-drawings/chart-drawing-record'
import type { DrawingToolId } from '../chart-drawings/drawing-tool'
import type { ChartAppearance } from '../chart-settings/chart-appearance-preference'
import type { OhlcBar } from '../contracts/OhlcBar'
import { lightweightChartOptions } from './lightweight-chart-options'
import './market-candlestick-chart.css'

type MarketCandlestickChartProps = {
  bars: OhlcBar[]
  precision: number
  theme: ColorTheme
  appearance: ChartAppearance
  timeDisplay: TimeDisplayPreference
  activeDrawingTool: DrawingToolId | null
  drawings: ChartDrawingRecord[]
  selectedDrawingId: string | null
  onSelectDrawing: (drawingId: string | null) => void
  onCreateDrawing: (tool: DrawingToolId, points: ChartDrawingPoint[]) => string
  onUpdateDrawingPoint: (drawingId: string, pointIndex: number, point: ChartDrawingPoint, persist: boolean) => void
  onUpdatePositionWidth: (drawingId: string, time: ChartDrawingPoint['time'], persist: boolean) => void
  onExitDrawingMode: () => void
  onDataApplied: (barCount: number) => void
  renderChartOverlay?: (
    chartApi: IChartApi,
    seriesApi: ISeriesApi<'Candlestick', Time>,
  ) => ReactNode
}

export function MarketCandlestickChart({
  bars,
  precision,
  theme,
  appearance,
  timeDisplay,
  activeDrawingTool,
  drawings,
  selectedDrawingId,
  onSelectDrawing,
  onCreateDrawing,
  onUpdateDrawingPoint,
  onUpdatePositionWidth,
  onExitDrawingMode,
  onDataApplied,
  renderChartOverlay,
}: MarketCandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const initialAppearanceRef = useRef(appearance)
  const initialTimeDisplayRef = useRef(timeDisplay)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick', Time> | null>(null)
  const [chartApi, setChartApi] = useState<IChartApi | null>(null)
  const [seriesApi, setSeriesApi] = useState<ISeriesApi<'Candlestick', Time> | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const initialAppearance = initialAppearanceRef.current
    const chart = createChart(container, lightweightChartOptions(initialAppearance, initialTimeDisplayRef.current))
    const series = chart.addSeries(CandlestickSeries, {
      upColor: initialAppearance.upCandleColor,
      downColor: initialAppearance.downCandleColor,
      borderUpColor: initialAppearance.upCandleColor,
      borderDownColor: initialAppearance.downCandleColor,
      wickUpColor: initialAppearance.upCandleColor,
      wickDownColor: initialAppearance.downCandleColor,
      priceLineColor: initialAppearance.priceLineColor,
    })

    chartRef.current = chart
    seriesRef.current = series
    setChartApi(chart)
    setSeriesApi(series)

    return () => {
      seriesRef.current = null
      chartRef.current = null
      setChartApi(null)
      setSeriesApi(null)
      chart.remove()
    }
  }, [])

  useEffect(() => {
    chartRef.current?.applyOptions(lightweightChartOptions(appearance, timeDisplay))
    seriesRef.current?.applyOptions({
      upColor: appearance.upCandleColor,
      downColor: appearance.downCandleColor,
      borderUpColor: appearance.upCandleColor,
      borderDownColor: appearance.downCandleColor,
      wickUpColor: appearance.upCandleColor,
      wickDownColor: appearance.downCandleColor,
      priceLineColor: appearance.priceLineColor,
    })
  }, [appearance, theme, timeDisplay])

  useEffect(() => {
    const series = seriesRef.current
    const chart = chartRef.current
    if (!series || !chart) return

    series.applyOptions({
      priceFormat: {
        type: 'price',
        precision,
        minMove: 10 ** -precision,
      },
    })
    series.setData(bars)
    chart.priceScale('right').applyOptions({ autoScale: true })
    chart.timeScale().fitContent()
    onDataApplied(bars.length)
  }, [bars, onDataApplied, precision])

  return (
    <div className="market-chart-host">
      <div ref={containerRef} className="market-chart-canvas" aria-label="Candlestick chart" />
      {chartApi && seriesApi && renderChartOverlay?.(chartApi, seriesApi)}
      {chartApi && seriesApi && (
        <ChartDrawingOverlay
          key={activeDrawingTool ?? 'chart-navigation'}
          chartApi={chartApi}
          seriesApi={seriesApi}
          activeTool={activeDrawingTool}
          drawings={drawings}
          selectedDrawingId={selectedDrawingId}
          onSelectDrawing={onSelectDrawing}
          onCreateDrawing={onCreateDrawing}
          onUpdateDrawingPoint={onUpdateDrawingPoint}
          onUpdatePositionWidth={onUpdatePositionWidth}
          onExitDrawingMode={onExitDrawingMode}
        />
      )}
    </div>
  )
}
