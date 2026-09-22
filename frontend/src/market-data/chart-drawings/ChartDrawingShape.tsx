import type { ChartDrawingRecord } from './chart-drawing-record'
import type { ChartDrawingScreenPoint } from './chart-drawing-screen-point'

type ChartDrawingShapeProps = {
  drawing: ChartDrawingRecord
  points: ChartDrawingScreenPoint[]
  width: number
  height: number
  precision?: number
}

function PositionDrawing({ points, width, height, precision = 5 }: Pick<ChartDrawingShapeProps, 'points' | 'width' | 'height' | 'precision'>) {
  const entry = points[0]
  const target = points[1]
  const stop = points[2]
  if (!entry || !target || !stop) return null

  const left = Math.min(entry.x, target.x)
  const right = Math.max(entry.x, target.x)
  const positionWidth = Math.max(2, right - left)
  const reward = Math.abs(target.price - entry.price)
  const risk = Math.max(Math.abs(entry.price - stop.price), Number.EPSILON)
  const rewardPercent = (reward / entry.price) * 100
  const riskPercent = (risk / entry.price) * 100

  const point = 10 ** -precision
  const isGold = entry.price > 500 || (precision === 2 && entry.price > 100)
  const pipSize = isGold
    ? 0.10
    : (precision === 5 || precision === 3)
      ? point * 10
      : point
  const rewardPips = reward / pipSize
  const riskPips = risk / pipSize
  const riskReward = reward / risk
  const targetTop = Math.min(target.y, entry.y)
  const targetHeight = Math.abs(entry.y - target.y)
  const stopTop = Math.min(stop.y, entry.y)
  const stopHeight = Math.abs(stop.y - entry.y)
  const boxTop = Math.min(target.y, stop.y, entry.y)
  const boxBottom = Math.max(target.y, stop.y, entry.y)
  const boxHeight = Math.max(2, boxBottom - boxTop)
  const isTargetAbove = target.y <= entry.y
  const targetLabelX = Math.min(Math.max(2, left + 4), Math.max(2, width - 277))
  const stopLabelX = Math.min(Math.max(2, left + 4), Math.max(2, width - 262))
  const targetLabelY = isTargetAbove
    ? Math.max(2, target.y - 21)
    : Math.min(Math.max(2, target.y + 2), height - 21)
  const stopLabelY = isTargetAbove
    ? Math.min(Math.max(2, stop.y + 2), height - 21)
    : Math.max(2, stop.y - 21)
  const centerLabelX = Math.min(
    Math.max(2, left + positionWidth / 2 - 94),
    Math.max(2, width - 190),
  )

  return (
    <g>
      <rect className="position-target-area" x={left} y={targetTop} width={positionWidth} height={targetHeight} />
      <rect className="position-stop-area" x={left} y={stopTop} width={positionWidth} height={stopHeight} />
      <rect className="position-outline" x={left} y={boxTop} width={positionWidth} height={boxHeight} />
      <line className="position-entry-line" x1={left} y1={entry.y} x2={right} y2={entry.y} />

      <g transform={`translate(${targetLabelX} ${targetLabelY})`}>
        <rect className="position-label-background target" width="275" height="19" rx="3" />
        <text className="position-label-text" x="5" y="13">
          Target: {reward.toFixed(precision)} ({rewardPercent.toFixed(3)}%) {rewardPips.toFixed(1)} pips
        </text>
      </g>

      <g transform={`translate(${centerLabelX} ${entry.y - 18})`}>
        <rect className="position-label-background entry" width="188" height="36" rx="4" />
        <text className="position-label-text" textAnchor="middle" x="94" y="14">Open P&amp;L: 0.00000, Qty: 1,000</text>
        <text className="position-label-text" textAnchor="middle" x="94" y="28">Risk/Reward ratio: {riskReward.toFixed(2)}</text>
      </g>

      <g transform={`translate(${stopLabelX} ${stopLabelY})`}>
        <rect className="position-label-background stop" width="260" height="19" rx="3" />
        <text className="position-label-text" x="5" y="13">
          Stop: {risk.toFixed(precision)} ({riskPercent.toFixed(3)}%) {riskPips.toFixed(1)} pips
        </text>
      </g>
    </g>
  )
}

export function ChartDrawingShape({ drawing, points, width, height, precision = 5 }: ChartDrawingShapeProps) {
  const first = points[0]
  const last = points.at(-1) ?? first
  if (!first || !last) return null

  const left = Math.min(first.x, last.x)
  const top = Math.min(first.y, last.y)
  const shapeWidth = Math.abs(last.x - first.x)
  const shapeHeight = Math.abs(last.y - first.y)

  switch (drawing.tool) {
    case 'trend-line':
      return (
        <g>
          <line className="drawing-hit-area" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
          <line className="drawing-stroke" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
        </g>
      )
    case 'arrow':
      return (
        <g>
          <line className="drawing-hit-area" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
          <line className="drawing-stroke" markerEnd="url(#drawing-arrow)" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
        </g>
      )
    case 'rectangle':
      return <rect className="drawing-stroke drawing-fill" x={left} y={top} width={shapeWidth} height={shapeHeight} />
    case 'circle':
      return <ellipse className="drawing-stroke drawing-fill" cx={(first.x + last.x) / 2} cy={(first.y + last.y) / 2} rx={shapeWidth / 2} ry={shapeHeight / 2} />
    case 'horizontal-line':
      return (
        <g>
          <line className="drawing-hit-area" x1={0} y1={first.y} x2={width} y2={first.y} />
          <line className="drawing-stroke" x1={0} y1={first.y} x2={width} y2={first.y} />
        </g>
      )
    case 'vertical-line':
      return (
        <g>
          <line className="drawing-hit-area" x1={first.x} y1={0} x2={first.x} y2={height} />
          <line className="drawing-stroke" x1={first.x} y1={0} x2={first.x} y2={height} />
        </g>
      )
    case 'parallel-channel': {
      const offset = 22
      return (
        <g className="drawing-stroke">
          <line x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
          <line x1={first.x} y1={first.y + offset} x2={last.x} y2={last.y + offset} />
          <line x1={first.x} y1={first.y} x2={first.x} y2={first.y + offset} />
          <line x1={last.x} y1={last.y} x2={last.x} y2={last.y + offset} />
        </g>
      )
    }
    case 'path':
      return (
        <g>
          <polyline className="drawing-hit-area" points={points.map((point) => `${point.x},${point.y}`).join(' ')} />
          <polyline className="drawing-stroke" points={points.map((point) => `${point.x},${point.y}`).join(' ')} />
        </g>
      )
    case 'text':
      return (
        <g>
          <rect
            x={first.x}
            y={first.y - 20}
            width={Math.max(50, ((drawing.text?.length ?? 4) + 1) * 9)}
            height={24}
            fill="transparent"
            className="drawing-hit-area"
          />
          <text className="drawing-text" x={first.x + 5} y={first.y - 6}>
            {drawing.text && drawing.text.trim() !== '' ? drawing.text : 'Text'}
          </text>
        </g>
      )
    case 'price-note':
      return (
        <g>
          <circle className="drawing-note-dot" cx={first.x} cy={first.y} r={3} />
          <text className="drawing-note" x={first.x + 7} y={first.y + 4}>{first.price.toFixed(precision)}</text>
        </g>
      )
    case 'long-position':
    case 'short-position':
      return <PositionDrawing points={points} width={width} height={height} precision={precision} />
    case 'fib-retracement': {
      const ratios = [0, 0.236, 0.382, 0.5, 0.618, 1]
      return (
        <g>
          {ratios.map((ratio) => {
            const y = first.y + (last.y - first.y) * ratio
            return (
              <g key={ratio}>
                <line className="drawing-fib-line" x1={left} y1={y} x2={left + shapeWidth} y2={y} />
                <text className="drawing-fib-label" x={left + 3} y={y - 3}>{ratio}</text>
              </g>
            )
          })}
        </g>
      )
    }
    case 'date-price-range':
      return (
        <g>
          <rect className="drawing-range" x={left} y={top} width={shapeWidth} height={shapeHeight} />
          <text className="drawing-range-label" x={left + 5} y={top + 14}>Δ {Math.abs(last.price - first.price).toFixed(5)}</text>
        </g>
      )
  }
}
