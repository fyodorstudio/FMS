import { useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react'
import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import { ChartDrawingShape } from './ChartDrawingShape'
import { ChartDrawingSelectionHandles, type DrawingHandleKind } from './ChartDrawingSelectionHandles'
import type { ChartDrawingPoint, ChartDrawingRecord } from './chart-drawing-record'
import type { ChartDrawingScreenPoint } from './chart-drawing-screen-point'
import { drawingTools, type DrawingToolId } from './drawing-tool'
import { normalizeDrawingPoints } from './position-drawing-geometry'
import './chart-drawing-overlay.css'

type ChartDrawingOverlayProps = {
  chartApi: IChartApi
  seriesApi: ISeriesApi<'Candlestick', Time>
  activeTool: DrawingToolId | null
  drawings: ChartDrawingRecord[]
  selectedDrawingId: string | null
  onSelectDrawing: (drawingId: string | null) => void
  onCreateDrawing: (tool: DrawingToolId, points: ChartDrawingPoint[]) => string
  onUpdateDrawingPoint: (drawingId: string, pointIndex: number, point: ChartDrawingPoint, persist: boolean) => void
  onUpdatePositionWidth: (drawingId: string, time: ChartDrawingPoint['time'], persist: boolean) => void
  onExitDrawingMode: () => void
}

type EditingHandle = {
  drawingId: string
  pointIndex: number
  kind: DrawingHandleKind
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
  onExitDrawingMode,
}: ChartDrawingOverlayProps) {
  const overlayRef = useRef<SVGSVGElement>(null)
  const dragDraftRef = useRef<ChartDrawingPoint[]>([])
  const pathPointsRef = useRef<ChartDrawingPoint[]>([])
  const editingHandleRef = useRef<EditingHandle | null>(null)
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
    return { time, price } as ChartDrawingPoint
  }

  const toScreenPoints = (drawing: ChartDrawingRecord) => {
    const points = drawing.points.map((point) => {
      const x = chartApi.timeScale().timeToCoordinate(point.time)
      const y = seriesApi.priceToCoordinate(point.price)
      return x === null || y === null ? null : { x, y, price: point.price }
    })
    return points.some((point) => point === null) ? [] : points as ChartDrawingScreenPoint[]
  }

  const resetDraft = () => {
    dragDraftRef.current = []
    pathPointsRef.current = []
    setDraft([])
  }

  const createAndSelectDrawing = (tool: DrawingToolId, points: ChartDrawingPoint[]) => {
    const drawingId = onCreateDrawing(tool, normalizeDrawingPoints(tool, points))
    onSelectDrawing(drawingId)
    resetDraft()
  }

  const startInteraction = (event: ReactPointerEvent<SVGSVGElement>) => {
    if (event.button !== 0 || !activeTool || editingHandleRef.current) return
    const point = eventToDataPoint(event)
    if (!point) return
    const tool = drawingTools.find((candidate) => candidate.id === activeTool)
    if (!tool) return

    event.preventDefault()
    if (tool.gesture === 'path') {
      if (pathPointsRef.current.length === 0) onSelectDrawing(null)
      pathPointsRef.current = [...pathPointsRef.current, point]
      setDraft([...pathPointsRef.current, point])
      return
    }

    if (tool.gesture === 'point') {
      createAndSelectDrawing(activeTool, [point])
      return
    }

    onSelectDrawing(null)
    event.currentTarget.setPointerCapture(event.pointerId)
    dragDraftRef.current = [point, point]
    setDraft(dragDraftRef.current)
  }

  const continueInteraction = (event: ReactPointerEvent<SVGSVGElement>) => {
    const point = eventToDataPoint(event)
    if (!point) return

    const editing = editingHandleRef.current
    if (editing) {
      if (editing.kind === 'position-width') {
        onUpdatePositionWidth(editing.drawingId, point.time, false)
      } else if (editing.kind === 'position-price') {
        const drawing = drawings.find((candidate) => candidate.id === editing.drawingId)
        const original = drawing?.points[editing.pointIndex]
        if (original) onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, { time: original.time, price: point.price }, false)
      } else {
        onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, point, false)
      }
      return
    }

    if (activeTool === 'path' && pathPointsRef.current.length > 0) {
      setDraft([...pathPointsRef.current, point])
      return
    }

    if (!activeTool || dragDraftRef.current.length === 0) return
    dragDraftRef.current = [dragDraftRef.current[0], point]
    setDraft(dragDraftRef.current)
  }

  const finishInteraction = (event: ReactPointerEvent<SVGSVGElement>) => {
    const point = eventToDataPoint(event)
    const editing = editingHandleRef.current
    if (editing) {
      if (point) {
        if (editing.kind === 'position-width') {
          onUpdatePositionWidth(editing.drawingId, point.time, true)
        } else if (editing.kind === 'position-price') {
          const drawing = drawings.find((candidate) => candidate.id === editing.drawingId)
          const original = drawing?.points[editing.pointIndex]
          if (original) onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, { time: original.time, price: point.price }, true)
        } else {
          onUpdateDrawingPoint(editing.drawingId, editing.pointIndex, point, true)
        }
      }
      editingHandleRef.current = null
      return
    }

    if (!activeTool || activeTool === 'path' || dragDraftRef.current.length === 0) return
    const completed = point ? [dragDraftRef.current[0], point] : dragDraftRef.current
    createAndSelectDrawing(activeTool, completed)
  }

  const cancelInteraction = () => {
    editingHandleRef.current = null
    dragDraftRef.current = []
    setDraft(pathPointsRef.current)
  }

  const handleContextMenu = (event: ReactPointerEvent<SVGSVGElement>) => {
    event.preventDefault()
    if (activeTool === 'path' && pathPointsRef.current.length >= 2) {
      createAndSelectDrawing('path', pathPointsRef.current)
    } else if (activeTool) {
      resetDraft()
    } else {
      resetDraft()
      onSelectDrawing(null)
    }
    editingHandleRef.current = null
    onExitDrawingMode()
  }

  const startHandleEdit = (
    event: ReactPointerEvent<SVGCircleElement>,
    drawingId: string,
    pointIndex: number,
    kind: DrawingHandleKind = 'point',
  ) => {
    if (event.button !== 0) return
    event.preventDefault()
    event.stopPropagation()
    event.currentTarget.setPointerCapture(event.pointerId)
    editingHandleRef.current = { drawingId, pointIndex, kind }
    onSelectDrawing(drawingId)
  }

  const normalizedDraft = activeTool ? normalizeDrawingPoints(activeTool, draft) : draft
  const draftDrawing: ChartDrawingRecord | null = activeTool && normalizedDraft.length > 0
    ? { id: 'draft', symbol: '', timeframe: 'H4', tool: activeTool, points: normalizedDraft, createdAt: 0 }
    : null

  return (
    <svg
      ref={overlayRef}
      className={`chart-drawing-overlay${activeTool ? ' drawing-active' : ''}`}
      onPointerDown={startInteraction}
      onPointerMove={continueInteraction}
      onPointerUp={finishInteraction}
      onPointerCancel={cancelInteraction}
      onContextMenu={handleContextMenu}
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
              if (activeTool || event.button !== 0) return
              event.stopPropagation()
              onSelectDrawing(drawing.id)
            }}
          >
            <ChartDrawingShape drawing={drawing} points={screenPoints} width={viewport.width} height={viewport.height} />
            {selected && (
              <ChartDrawingSelectionHandles
                drawing={drawing}
                screenPoints={screenPoints}
                viewport={viewport}
                onStartHandleEdit={startHandleEdit}
              />
            )}
          </g>
        )
      })}
      {draftDrawing && (
        <g className="drawing-draft">
          <ChartDrawingShape drawing={draftDrawing} points={toScreenPoints(draftDrawing)} width={viewport.width} height={viewport.height} />
          {activeTool === 'path' && draft.length > 0 && (() => {
            const draftPoints = toScreenPoints(draftDrawing)
            const last = draftPoints.at(-1)
            return last ? <circle className="drawing-ghost-point" cx={last.x} cy={last.y} r="4" /> : null
          })()}
        </g>
      )}
    </svg>
  )
}
