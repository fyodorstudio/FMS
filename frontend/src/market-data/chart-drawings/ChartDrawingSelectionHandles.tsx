import type { PointerEvent as ReactPointerEvent } from 'react'
import type { ChartDrawingRecord } from './chart-drawing-record'
import type { ChartDrawingScreenPoint } from './chart-drawing-screen-point'

export type DrawingHandleKind = 'point' | 'position-price' | 'position-width'

type ChartDrawingSelectionHandlesProps = {
  drawing: ChartDrawingRecord
  screenPoints: ChartDrawingScreenPoint[]
  viewport: { width: number; height: number }
  onStartHandleEdit: (
    event: ReactPointerEvent<SVGCircleElement>,
    drawingId: string,
    pointIndex: number,
    kind?: DrawingHandleKind,
  ) => void
}

function handlePoint(
  drawing: ChartDrawingRecord,
  point: ChartDrawingScreenPoint,
  pointIndex: number,
  screenPoints: ChartDrawingScreenPoint[],
  viewport: { width: number; height: number },
) {
  if (drawing.tool === 'horizontal-line') return { ...point, x: viewport.width / 2 }
  if (drawing.tool === 'vertical-line') return { ...point, y: viewport.height / 2 }
  if ((drawing.tool === 'long-position' || drawing.tool === 'short-position') && pointIndex > 0 && screenPoints[0]) {
    return { ...point, x: screenPoints[0].x }
  }
  return point
}

export function ChartDrawingSelectionHandles({
  drawing,
  screenPoints,
  viewport,
  onStartHandleEdit,
}: ChartDrawingSelectionHandlesProps) {
  const isPosition = drawing.tool === 'long-position' || drawing.tool === 'short-position'
  return (
    <>
      {screenPoints.map((point, pointIndex) => {
        const displayedPoint = handlePoint(drawing, point, pointIndex, screenPoints, viewport)
        return (
          <circle
            className="drawing-resize-handle"
            key={`${drawing.id}-${pointIndex}`}
            cx={displayedPoint.x}
            cy={displayedPoint.y}
            r="5"
            onPointerDown={(event) => onStartHandleEdit(
              event,
              drawing.id,
              pointIndex,
              isPosition && pointIndex > 0 ? 'position-price' : 'point',
            )}
          />
        )
      })}
      {isPosition && screenPoints[0] && screenPoints[1] && (
        <circle
          className="drawing-resize-handle"
          cx={screenPoints[1].x}
          cy={screenPoints[0].y}
          r="5"
          onPointerDown={(event) => onStartHandleEdit(event, drawing.id, 1, 'position-width')}
        />
      )}
    </>
  )
}
