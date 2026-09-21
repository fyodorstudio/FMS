import { useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react'
import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { ChartDrawingShape } from './ChartDrawingShape'
import type { ChartDrawingPoint, ChartDrawingRecord } from './chart-drawing-record'
import type { ChartDrawingScreenPoint } from './chart-drawing-screen-point'
import { drawingTools, type DrawingToolId } from './drawing-tool'
import './chart-drawing-overlay.css'

type ChartDrawingOverlayProps = {
  chartApi: IChartApi
  seriesApi: ISeriesApi<'Candlestick', Time>
  activeTool: DrawingToolId | null
  drawings: ChartDrawingRecord[]
  selectedDrawingId: string | null
  onSelectDrawing: (drawingId: string | null) => void
  onCreateDrawing: (tool: DrawingToolId, points: ChartDrawingPoint[]) => void
  onUpdateDrawingPoint: (drawingId: string, pointIndex: number, point: ChartDrawingPoint, persist: boolean) => void
  onUpdatePositionWidth: (drawingId: string, time: ChartDrawingPoint['time'], persist: boolean) => void
}

type EditingHandle = {
  drawingId: string
  pointIndex: number
  kind: 'point' | 'position-width'
}

export function ChartDrawingOverlay({
  chartApi,
  seriesApi,
  activeTool,
  drawings,
  selectedDrawingId,
  onSelectDrawing,
  onCreateDrawing,
  onUpdateDrawingPoint,
  onUpdatePositionWidth,
}: ChartDrawingOverlayProps) {
  const overlayRef = useRef<SVGSVGElement>(null)
  const draftRef = useRef<ChartDrawingPoint[]>([])
  const editingHandleRef = useRef<EditingHandle | null>(null)
  const lastPathPointer = useRef<{ x: number; y: number } | null>(null)
  const [draft, setDraft] = useState<ChartDrawingPoint[]>([])
  const [viewport, setViewport] = useState({ width: 0, height: 0, revision: 0 })

  useEffect(() => {
    const overlay = overlayRef.current
    if (!overlay) return
    const refresh = () => setViewport((current) => ({
      width: overlay.clientWidth,
      height: overlay.clientHeight,
      revision: current.revision + 1,
    }))
    const resizeObserver = new ResizeObserver(refresh)
    resizeObserver.observe(overlay)
    chartApi.timeScale().subscribeVisibleLogicalRangeChange(refresh)
    refresh()
    return () => {
      resizeObserver.disconnect()
      chartApi.timeScale().unsubscribeVisibleLogicalRangeChange(refresh)
    }
  }, [chartApi])

  const eventToDataPoint = (event: ReactPointerEvent<SVGSVGElement>) => {
    const rectangle = event.currentTarget.getBoundingClientRect()
    const x = event.clientX - rectangle.left
    const y = event.clientY - rectangle.top
    const time = chartApi.timeScale().coordinateToTime(x)
    const price = seriesApi.coordinateToPrice(y)
    if (typeof time !== 'number' || price === null) return null
    return { point: { time, price } as ChartDrawingPoint, screen: { x, y } }
  }

  const toScreenPoints = (drawing: ChartDrawingRecord) => {
    const points = drawing.points.map((point) => {
      const x = chartApi.timeScale().timeToCoordinate(point.time)
      const y = seriesApi.priceToCoordinate(point.price)
      return x === null || y === null ? null : { x, y, price: point.price }
    })
    return points.some((point) => point === null) ? [] : points as ChartDrawingScreenPoint[]
  }

  const startDrawing = (event: ReactPointerEvent<SVGSVGElement>) => {
    if (!activeTool || editingHandleRef.current) return
    const converted = eventToDataPoint(event)
    if (!converted) return
    const tool = drawingTools.find((candidate) => candidate.id === activeTool)
    if (!tool) return

    event.preventDefault()
    onSelectDrawing(null)
    if (tool.gesture === 'point') {
      onCreateDrawing(activeTool, [converted.point])
      return
    }

    event.currentTarget.setPointerCapture(event.pointerId)
    draftRef.current = [converted.point]
    setDraft(draftRef.current)
    lastPathPointer.current = converted.screen
  }

  const continueInteraction = (event: ReactPointerEvent<SVGSVGElement>) => {
    const converted = eventToDataPoint(event)
    if (!converted) return

    const editing = editingHandleRef.current
    if (editing) {
      if (editing.kind === 'position-width') {
        onUpdatePositionWidth(editing.drawingId, converted.point.time, false)
      } else {
        onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, converted.point, false)
      }
      return
    }

    if (!activeTool || draftRef.current.length === 0) return
    const tool = drawingTools.find((candidate) => candidate.id === activeTool)
    if (!tool) return

    if (tool.gesture === 'path') {
      const previous = lastPathPointer.current
      if (previous && Math.hypot(converted.screen.x - previous.x, converted.screen.y - previous.y) < 4) return
      lastPathPointer.current = converted.screen
      draftRef.current = [...draftRef.current, converted.point]
    } else {
      draftRef.current = [draftRef.current[0], converted.point]
    }
    setDraft(draftRef.current)
  }

  const finishInteraction = (event: ReactPointerEvent<SVGSVGElement>) => {
    const converted = eventToDataPoint(event)
    const editing = editingHandleRef.current
    if (editing) {
      if (converted) {
        if (editing.kind === 'position-width') {
          onUpdatePositionWidth(editing.drawingId, converted.point.time, true)
        } else {
          onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, converted.point, true)
        }
      }
      editingHandleRef.current = null
      return
    }

    if (!activeTool || draftRef.current.length === 0) return
    continueInteraction(event)
    const completed = draftRef.current
    draftRef.current = []
    lastPathPointer.current = null
    setDraft([])
    if (completed.length >= 2) onCreateDrawing(activeTool, completed)
  }

  const startHandleEdit = (
    event: ReactPointerEvent<SVGCircleElement>,
    drawingId: string,
    pointIndex: number,
    kind: EditingHandle['kind'] = 'point',
  ) => {
    event.preventDefault()
    event.stopPropagation()
    event.currentTarget.setPointerCapture(event.pointerId)
    editingHandleRef.current = { drawingId, pointIndex, kind }
    onSelectDrawing(drawingId)
  }

  const draftDrawing: ChartDrawingRecord | null = activeTool && draft.length > 0
    ? { id: 'draft', symbol: '', timeframe: 'H4', tool: activeTool, points: draft, createdAt: 0 }
    : null

  return (
    <svg
      ref={overlayRef}
      className={`chart-drawing-overlay${activeTool ? ' drawing-active' : ''}`}
      onPointerDown={startDrawing}
      onPointerMove={continueInteraction}
      onPointerUp={finishInteraction}
      onPointerCancel={finishInteraction}
      aria-label={activeTool ? `Draw with ${activeTool}` : 'Saved chart drawings'}
    >
      <defs>
        <marker id="drawing-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" className="drawing-arrow-head" />
        </marker>
      </defs>
      {drawings.map((drawing) => {
        const screenPoints = toScreenPoints(drawing)
        const selected = drawing.id === selectedDrawingId
        return (
          <g
            key={drawing.id}
            className={`drawing-object${selected ? ' selected' : ''}`}
            onPointerDown={(event) => {
              if (activeTool) return
              event.stopPropagation()
              onSelectDrawing(drawing.id)
            }}
          >
            <ChartDrawingShape drawing={drawing} points={screenPoints} width={viewport.width} height={viewport.height} />
            {selected && screenPoints.map((point, pointIndex) => (
              <circle
                className="drawing-resize-handle"
                key={`${drawing.id}-${pointIndex}`}
                cx={point.x}
                cy={point.y}
                r="5"
                onPointerDown={(event) => startHandleEdit(event, drawing.id, pointIndex)}
              />
            ))}
            {selected && (drawing.tool === 'long-position' || drawing.tool === 'short-position') && screenPoints[0] && screenPoints[1] && (
              <circle
                className="drawing-resize-handle"
                cx={screenPoints[1].x}
                cy={screenPoints[0].y}
                r="5"
                onPointerDown={(event) => startHandleEdit(event, drawing.id, 1, 'position-width')}
              />
            )}
          </g>
        )
      })}
      {draftDrawing && (
        <g className="drawing-draft">
          <ChartDrawingShape drawing={draftDrawing} points={toScreenPoints(draftDrawing)} width={viewport.width} height={viewport.height} />
        </g>
      )}
    </svg>
  )
}
