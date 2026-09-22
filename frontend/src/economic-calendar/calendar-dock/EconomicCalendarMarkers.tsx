import { useEffect, useMemo, useRef, useState } from 'react'
import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts'
import type { OhlcBar } from '../../market-data/contracts/OhlcBar'
import type { EconomicCalendarEvent } from '../mt5-calendar/calendar-contract'
import './economic-calendar-markers.css'

type EconomicCalendarMarkersProps = {
  chartApi: IChartApi
  seriesApi: ISeriesApi<'Candlestick', Time>
  symbol: string
  bars: OhlcBar[]
  events: EconomicCalendarEvent[]
  onSelectEvent?: (event: EconomicCalendarEvent) => void
}

type EventGroup = {
  id: string
  currency: string
  barTime: number
  highestImportance: 'high' | 'medium'
  events: EconomicCalendarEvent[]
}

type PositionedGroup = EventGroup & {
  x: number
}

function symbolCurrencies(symbol: string): Set<string> {
  const currencies = new Set<string>()
  const clean = symbol.replace(/[^A-Za-z]/g, '').toUpperCase()
  if (clean.length >= 6) {
    currencies.add(clean.slice(0, 3))
    currencies.add(clean.slice(3, 6))
  } else if (clean.length === 3) {
    currencies.add(clean)
  }
  return currencies
}

function findNearestBarTime(eventSec: number, barTimes: number[]): number {
  if (barTimes.length === 0) return eventSec
  let low = 0
  let high = barTimes.length - 1
  let best = barTimes[0]
  while (low <= high) {
    const mid = Math.floor((low + high) / 2)
    const current = barTimes[mid]
    if (Math.abs(current - eventSec) < Math.abs(best - eventSec)) {
      best = current
    }
    if (current < eventSec) {
      low = mid + 1
    } else {
      high = mid - 1
    }
  }
  return best
}

export function EconomicCalendarMarkers({
  chartApi,
  symbol,
  bars,
  events,
  onSelectEvent,
}: EconomicCalendarMarkersProps) {
  const stripRef = useRef<HTMLDivElement>(null)
  const [hoveredGroupId, setHoveredGroupId] = useState<string | null>(null)
  const [revision, setRevision] = useState(0)

  const eventGroups = useMemo(() => {
    if (bars.length === 0 || events.length === 0) return []
    const currencies = symbolCurrencies(symbol)
    const minBarTime = Number(bars[0].time)
    const maxBarTime = Number(bars[bars.length - 1].time)
    const barTimes = bars.map((b) => Number(b.time))

    const map = new Map<string, EventGroup>()

    for (const event of events) {
      if (!event.release_at) continue
      if (event.importance !== 'high' && event.importance !== 'medium') continue
      const currency = event.currency.toUpperCase()
      if (!currencies.has(currency)) continue

      const eventSec = Math.floor(event.release_at / 1000)
      if (eventSec < minBarTime - 86400 || eventSec > maxBarTime + 86400) continue

      const barTime = findNearestBarTime(eventSec, barTimes)
      const groupKey = `${currency}-${barTime}`

      const existing = map.get(groupKey)
      if (existing) {
        existing.events.push(event)
        if (event.importance === 'high') existing.highestImportance = 'high'
      } else {
        map.set(groupKey, {
          id: groupKey,
          currency,
          barTime,
          highestImportance: event.importance,
          events: [event],
        })
      }
    }

    return Array.from(map.values())
  }, [bars, events, symbol])

  const [containerWidth, setContainerWidth] = useState(800)

  useEffect(() => {
    const strip = stripRef.current
    if (!strip) return
    const updateWidth = () => setContainerWidth(strip.clientWidth)
    updateWidth()
    const observer = new ResizeObserver(updateWidth)
    observer.observe(strip)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const handleRangeChange = () => setRevision((rev) => rev + 1)
    chartApi.timeScale().subscribeVisibleLogicalRangeChange(handleRangeChange)
    chartApi.timeScale().subscribeVisibleTimeRangeChange(handleRangeChange)
    return () => {
      chartApi.timeScale().unsubscribeVisibleLogicalRangeChange(handleRangeChange)
      chartApi.timeScale().unsubscribeVisibleTimeRangeChange(handleRangeChange)
    }
  }, [chartApi])

  const positionedGroups = useMemo(() => {
    // depend on revision to trigger recalculation on pan/zoom
    void revision
    const timeScale = chartApi.timeScale()

    const results: PositionedGroup[] = []
    for (const group of eventGroups) {
      const coord = timeScale.timeToCoordinate(group.barTime as unknown as Time)
      if (coord === null || coord < 20 || coord > containerWidth - 10) continue
      results.push({ ...group, x: coord })
    }
    return results
  }, [chartApi, containerWidth, eventGroups, revision])

  if (positionedGroups.length === 0) {
    return <div ref={stripRef} className="calendar-markers-strip" />
  }

  const hoveredGroup = positionedGroups.find((g) => g.id === hoveredGroupId)

  return (
    <div ref={stripRef} className="calendar-markers-strip" aria-label="Economic calendar release timeline">
      {positionedGroups.map((group) => {
        const count = group.events.length
        return (
          <button
            key={group.id}
            type="button"
            className="calendar-marker-badge"
            style={{ left: `${group.x}px` }}
            onClick={() => onSelectEvent?.(group.events[0])}
            onMouseEnter={() => setHoveredGroupId(group.id)}
            onMouseLeave={() => setHoveredGroupId((curr) => (curr === group.id ? null : curr))}
            title={`View ${group.currency} economic releases in calendar dock`}
          >
            <span className={`calendar-marker-dot ${group.highestImportance}`} aria-hidden="true" />
            <span>{group.currency}</span>
            {count > 1 && <span className="calendar-marker-count">({count})</span>}
          </button>
        )
      })}

      {hoveredGroup && (
        <div
          className="calendar-marker-tooltip"
          style={{
            left: `${Math.min(Math.max(145, hoveredGroup.x), containerWidth - 145)}px`,
          }}
          role="tooltip"
        >
          <div className="calendar-tooltip-header">
            <span>{hoveredGroup.currency} Releases ({hoveredGroup.events.length})</span>
            <span>{new Date(hoveredGroup.barTime * 1000).toUTCString().slice(17, 22)} UTC</span>
          </div>
          {hoveredGroup.events.slice(0, 4).map((event) => (
            <div key={event.value_id} className="calendar-tooltip-item">
              <span className="calendar-tooltip-item-title">
                <span className={`calendar-marker-dot ${event.importance}`} aria-hidden="true" />
                {event.name}
              </span>
              <div className="calendar-tooltip-item-values">
                {event.actual !== null && <span>Act: {event.actual}</span>}
                {event.forecast !== null && <span>Frc: {event.forecast}</span>}
                {event.previous !== null && <span>Prev: {event.previous}</span>}
              </div>
            </div>
          ))}
          {hoveredGroup.events.length > 4 && (
            <span className="calendar-marker-count">+{hoveredGroup.events.length - 4} more releases</span>
          )}
          <span className="calendar-tooltip-hint">Click badge to jump to calendar table</span>
        </div>
      )}
    </div>
  )
}
