import type { FmsArrowFilter, FmsChartArrow } from '../placeholder-feed/fms-placeholder-types'
import './fms-arrow-controls.css'

type FmsArrowControlsProps = {
  visible: boolean
  filter: FmsArrowFilter
  arrows?: FmsChartArrow[]
  selectedArrowId?: string | null
  arrowCount: number
  onVisibleChange: (visible: boolean) => void
  onFilterChange: (filter: FmsArrowFilter) => void
  onSelectArrowId?: (arrowId: string | null) => void
}

export function FmsArrowControls({
  visible,
  filter,
  arrows = [],
  selectedArrowId,
  arrowCount,
  onVisibleChange,
  onFilterChange,
  onSelectArrowId,
}: FmsArrowControlsProps) {
  const currentValue = selectedArrowId ? `arrow:${selectedArrowId}` : filter

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value
    if (val.startsWith('arrow:')) {
      const arrowId = val.replace('arrow:', '')
      onSelectArrowId?.(arrowId)
    } else {
      onSelectArrowId?.(null)
      onFilterChange(val as FmsArrowFilter)
    }
  }

  return (
    <div className="fms-arrow-controls" aria-label="FMS chart arrows">
      <label>
        <input type="checkbox" checked={visible} onChange={(event) => onVisibleChange(event.target.checked)} />
        Past arrows <span>{arrowCount}</span>
      </label>
      <select
        aria-label="Filter or select FMS arrow"
        value={currentValue}
        onChange={handleChange}
        disabled={!visible}
      >
        <optgroup label="Filter Scope">
          <option value="all">All pair arrows ({arrows.length})</option>
          <option value="wins">Wins only</option>
          <option value="losses">Losses only</option>
          <option value="buys">BUY only</option>
          <option value="sells">SELL only</option>
        </optgroup>
        {arrows.length > 0 && (
          <optgroup label="Select Pair Arrow">
            {arrows.map((arr) => {
              const dateStr = new Date(arr.time * 1000).toLocaleDateString([], {
                month: 'short',
                day: 'numeric',
              })
              const resStr = arr.resultR != null
                ? (arr.resultR > 0 ? `+${arr.resultR.toFixed(2)}R` : `${arr.resultR.toFixed(2)}R`)
                : (arr.result === 'open' ? 'Open' : '')
              const label = `${dateStr} · ${arr.eventName || arr.setupName} (${arr.direction.toUpperCase()} ${resStr})`
              return (
                <option key={arr.id} value={`arrow:${arr.id}`}>
                  {label}
                </option>
              )
            })}
          </optgroup>
        )}
      </select>
    </div>
  )
}
