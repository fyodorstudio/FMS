import type { ChartDrawingRecord } from './chart-drawing-record'
import type { ChartDrawingScreenPoint } from './chart-drawing-screen-point'

type ChartDrawingShapeProps = {
  drawing: ChartDrawingRecord
  points: ChartDrawingScreenPoint[]
  width: number
  height: number
}

function PositionDrawing({ points, width, height }: Pick<ChartDrawingShapeProps, 'points' | 'width' | 'height'>) {
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
  const pipSize = entry.price > 20 ? 0.01 : 0.0001
  const rewardPips = reward / pipSize
  const riskPips = risk / pipSize
  const riskReward = reward / risk
  const targetTop = Math.min(target.y, entry.y)
  const targetHeight = Math.abs(entry.y - target.y)
  const stopTop = Math.min(stop.y, entry.y)
  const stopHeight = Math.abs(stop.y - entry.y)
  const targetLabelX = Math.min(Math.max(2, left + 4), Math.max(2, width - 277))
  const stopLabelX = Math.min(Math.max(2, left + 4), Math.max(2, width - 262))
  const targetLabelY = Math.max(2, target.y - 20)
  const stopLabelY = Math.min(Math.max(2, stop.y + 3), Math.max(2, height - 21))
  const centerLabelX = Math.min(
    Math.max(2, left + positionWidth / 2 - 94),
    Math.max(2, width - 190),
  )

  return (
    <g>
      <rect className="position-target-area" x={left} y={targetTop} width={positionWidth} height={targetHeight} />
      <rect className="position-stop-area" x={left} y={stopTop} width={positionWidth} height={stopHeight} />
      <rect className="position-outline" x={left} y={Math.min(target.y, stop.y)} width={positionWidth} height={Math.abs(stop.y - target.y)} />
      <line className="position-entry-line" x1={left} y1={entry.y} x2={right} y2={entry.y} />

      <g transform={`translate(${targetLabelX} ${targetLabelY})`}>
        <rect className="position-label-background target" width="275" height="19" rx="3" />
        <text className="position-label-text" x="5" y="13">
          Target: {reward.toFixed(5)} ({rewardPercent.toFixed(3)}%) {rewardPips.toFixed(1)}, Amount: {(100 + riskReward).toFixed(2)}
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
          Stop: {risk.toFixed(5)} ({riskPercent.toFixed(3)}%) {riskPips.toFixed(1)}, Amount: 99.00
        </text>
      </g>
    </g>
  )
}

export function ChartDrawingShape({ drawing, points, width, height }: ChartDrawingShapeProps) {
  const first = points[0]
  const last = points.at(-1) ?? first
  if (!first || !last) return null

  const left = Math.min(first.x, last.x)
  const top = Math.min(first.y, last.y)
  const shapeWidth = Math.abs(last.x - first.x)
  const shapeHeight = Math.abs(last.y - first.y)

  switch (drawing.tool) {
    case 'trend-line':
      return <line className="drawing-stroke" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
    case 'arrow':
      return <line className="drawing-stroke" markerEnd="url(#drawing-arrow)" x1={first.x} y1={first.y} x2={last.x} y2={last.y} />
    case 'rectangle':
      return <rect className="drawing-stroke drawing-fill" x={left} y={top} width={shapeWidth} height={shapeHeight} />
    case 'circle':
      return <ellipse className="drawing-stroke drawing-fill" cx={(first.x + last.x) / 2} cy={(first.y + last.y) / 2} rx={shapeWidth / 2} ry={shapeHeight / 2} />
    case 'horizontal-line':
      return <line className="drawing-stroke" x1={0} y1={first.y} x2={width} y2={first.y} />
    case 'vertical-line':
      return <line className="drawing-stroke" x1={first.x} y1={0} x2={first.x} y2={height} />
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
      return <polyline className="drawing-stroke" points={points.map((point) => `${point.x},${point.y}`).join(' ')} />
    case 'text':
      return <text className="drawing-text" x={first.x + 5} y={first.y - 6}>Text</text>
    case 'price-note':
      return (
        <g>
          <circle className="drawing-note-dot" cx={first.x} cy={first.y} r={3} />
          <text className="drawing-note" x={first.x + 7} y={first.y + 4}>{first.price.toFixed(5)}</text>
        </g>
      )
    case 'long-position':
    case 'short-position':
      return <PositionDrawing points={points} width={width} height={height} />
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
