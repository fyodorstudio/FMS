import type { FmsArrowFilter } from '../placeholder-feed/fms-placeholder-types'
import './fms-arrow-controls.css'

type FmsArrowControlsProps = {
  visible: boolean
  filter: FmsArrowFilter
  arrowCount: number
  onVisibleChange: (visible: boolean) => void
  onFilterChange: (filter: FmsArrowFilter) => void
}

export function FmsArrowControls({
  visible,
  filter,
  arrowCount,
  onVisibleChange,
  onFilterChange,
}: FmsArrowControlsProps) {
  return (
    <div className="fms-arrow-controls" aria-label="FMS chart arrows">
      <label>
        <input type="checkbox" checked={visible} onChange={(event) => onVisibleChange(event.target.checked)} />
        Past arrows <span>{arrowCount}</span>
      </label>
      <select
        aria-label="Filter FMS arrows"
        value={filter}
        onChange={(event) => onFilterChange(event.target.value as FmsArrowFilter)}
        disabled={!visible}
      >
        <option value="all">All arrows</option>
        <option value="wins">Wins</option>
        <option value="losses">Losses</option>
        <option value="v1">FMS v1</option>
        <option value="v2">FMS v2</option>
      </select>
      <em>Sample</em>
    </div>
  )
}
