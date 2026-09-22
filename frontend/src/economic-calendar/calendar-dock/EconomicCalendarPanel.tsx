import { useEffect, useMemo, useState } from 'react'
import {
  timeDisplayLabel,
  type TimeDisplayPreference,
} from '../../appearance/time-display/time-display-preference'
import type { CalendarSourceHealth } from '../../system-connectivity/bridge-status/bridge-contract'
import type { EconomicCalendarEvent } from '../mt5-calendar/calendar-contract'
import {
  calendarDisplayRange,
  displayDateKey,
  displayWeekDateKeys,
  type CalendarRangePreset,
} from './calendar-display-range'
import { VirtualizedCalendarRows } from './VirtualizedCalendarRows'
import './economic-calendar-panel.css'

type EconomicCalendarPanelProps = {
  events: EconomicCalendarEvent[]
  source: CalendarSourceHealth | null
  error: string | null
  clockOffsetMs: number
  timeDisplay: TimeDisplayPreference
  highlightedEventId?: string | null
  rangePreset?: CalendarRangePreset
  onRangePresetChange?: (preset: CalendarRangePreset) => void
}

function sourceLabel(source: CalendarSourceHealth | null, error: string | null) {
  if (error) return error
  if (!source) return 'Waiting for the local bridge'
  if (source.status === 'live') return `${source.event_count} MT5 events · live publisher`
  if (source.status === 'awaiting-snapshot') return 'Calendar EA connected · receiving atomic snapshot'
  if (source.status === 'stale') return 'Calendar EA heartbeat is stale'
  return 'Attach FyodorCalendarPublisher to one MT5 chart'
}

export function EconomicCalendarPanel({
  events,
  source,
  error,
  clockOffsetMs,
  timeDisplay,
  highlightedEventId,
  rangePreset: externalRangePreset,
  onRangePresetChange,
}: EconomicCalendarPanelProps) {
  const [now, setNow] = useState(() => Date.now() + clockOffsetMs)
  const initialToday = displayDateKey(now, timeDisplay)
  const initialWeek = displayWeekDateKeys(initialToday)
  const [internalRangePreset, setInternalRangePreset] = useState<CalendarRangePreset>('this-week')
  const rangePreset = externalRangePreset ?? internalRangePreset
  const setRangePreset = onRangePresetChange ?? setInternalRangePreset
  const [customFrom, setCustomFrom] = useState(initialWeek.start)
  const [customTo, setCustomTo] = useState(initialWeek.end)

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now() + clockOffsetMs), 1_000)
    return () => window.clearInterval(timer)
  }, [clockOffsetMs])

  const today = displayDateKey(now, timeDisplay)
  const range = useMemo(
    () => calendarDisplayRange(rangePreset, today, customFrom, customTo, timeDisplay),
    [customFrom, customTo, rangePreset, timeDisplay, today],
  )

  const orderedEvents = useMemo(() => {
    const list = events.filter((event) => {
      if (event.release_at === null) return false
      if (highlightedEventId && event.value_id === highlightedEventId) return true
      return range !== null && event.release_at >= range.from && event.release_at < range.to
    })
    return list.sort((left, right) => (left.release_at ?? Number.MAX_SAFE_INTEGER) - (right.release_at ?? Number.MAX_SAFE_INTEGER))
  }, [events, highlightedEventId, range])

  return (
    <section className="economic-calendar" aria-label="Economic Calendar">
      <div className="economic-calendar-heading">
        <div className="calendar-heading-copy">
          <strong>Economic Calendar</strong>
          <span>{sourceLabel(source, error)} · {timeDisplayLabel(timeDisplay)}</span>
        </div>
        <div className="calendar-range-controls">
          <label>
            <span>
              Range
              <span
                className="calendar-range-tooltip-hint"
                title="Also affects the chart timeline strip"
                aria-label="Also affects the chart timeline strip"
              >
                (?)
              </span>
            </span>
            <select value={rangePreset} onChange={(event) => setRangePreset(event.target.value as CalendarRangePreset)}>
              <option value="previous-week">Previous week</option>
              <option value="this-week">This week</option>
              <option value="next-week">Next week</option>
              <option value="custom">Custom</option>
            </select>
          </label>
          {rangePreset === 'custom' && (
            <div className="calendar-custom-range">
              <input aria-label="Calendar range start" type="date" value={customFrom} onChange={(event) => setCustomFrom(event.target.value)} />
              <span>to</span>
              <input aria-label="Calendar range end" type="date" value={customTo} onChange={(event) => setCustomTo(event.target.value)} />
            </div>
          )}
          <span className="calendar-visible-count">{orderedEvents.length} shown</span>
          <span className={`calendar-source-badge ${source?.status ?? 'waiting-for-publisher'}`}>
            {source?.status === 'live' ? 'MT5 LIVE' : source?.status.replaceAll('-', ' ').toUpperCase() ?? 'WAITING'}
          </span>
        </div>
      </div>

      <div className="calendar-table">
        <div className="calendar-row calendar-columns" aria-hidden="true">
          <span>Time</span><span>Countdown</span><span>Currency</span><span>Importance</span><span>Event</span><span>Actual</span><span>Forecast</span><span>Previous</span>
        </div>
        <VirtualizedCalendarRows
          events={orderedEvents}
          now={now}
          timeDisplay={timeDisplay}
          emptyLabel={range === null ? 'Choose a valid custom date range' : sourceLabel(source, error)}
          highlightedEventId={highlightedEventId}
        />
      </div>
    </section>
  )
}
