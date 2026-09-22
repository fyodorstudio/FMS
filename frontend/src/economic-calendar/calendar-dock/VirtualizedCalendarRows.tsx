import { useEffect, useRef, useState, type UIEvent } from 'react'
import { formatAppTimestamp, type TimeDisplayPreference } from '../../appearance/time-display/time-display-preference'
import type { EconomicCalendarEvent } from '../mt5-calendar/calendar-contract'

type VirtualizedCalendarRowsProps = {
  events: EconomicCalendarEvent[]
  now: number
  timeDisplay: TimeDisplayPreference
  emptyLabel: string
  highlightedEventId?: string | null
}

const rowHeight = 36
const overscan = 8
const multiplierSuffix: Record<number, string> = { 1: 'K', 2: 'M', 3: 'B', 4: 'T' }

function countdownLabel(releaseAt: number | null, actual: number | null, now: number) {
  if (actual !== null) return 'Released'
  if (releaseAt === null) return 'Time unavailable'
  const remaining = releaseAt - now
  if (remaining <= 0) return 'Awaiting actual'
  const seconds = Math.floor(remaining / 1_000)
  const days = Math.floor(seconds / 86_400)
  const hours = Math.floor(seconds % 86_400 / 3_600).toString().padStart(2, '0')
  const minutes = Math.floor(seconds % 3_600 / 60).toString().padStart(2, '0')
  const finalSeconds = (seconds % 60).toString().padStart(2, '0')
  return days > 0 ? `${days}d ${hours}:${minutes}:${finalSeconds}` : `${hours}:${minutes}:${finalSeconds}`
}

function formatValue(value: number | null, event: EconomicCalendarEvent) {
  if (value === null) return '—'
  const number = value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: Math.min(event.digits, 6),
  })
  if (event.unit === 1) return `${number}%`
  return `${number}${multiplierSuffix[event.multiplier] ?? ''}`
}

export function VirtualizedCalendarRows({
  events,
  now,
  timeDisplay,
  emptyLabel,
  highlightedEventId,
}: VirtualizedCalendarRowsProps) {
  const viewportRef = useRef<HTMLDivElement>(null)
  const [viewportHeight, setViewportHeight] = useState(0)
  const [scrollTop, setScrollTop] = useState(0)

  useEffect(() => {
    const viewport = viewportRef.current
    if (!viewport) return
    const updateHeight = () => setViewportHeight(viewport.clientHeight)
    updateHeight()
    const observer = new ResizeObserver(updateHeight)
    observer.observe(viewport)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!highlightedEventId || !viewportRef.current) return
    const index = events.findIndex((e) => e.value_id === highlightedEventId)
    if (index === -1) return
    const targetScroll = Math.max(0, index * rowHeight - (viewportHeight || 300) / 2 + rowHeight / 2)
    viewportRef.current.scrollTo({ top: targetScroll, behavior: 'smooth' })
  }, [events, highlightedEventId, viewportHeight])

  if (events.length === 0) {
    return <div className="calendar-rows"><p className="calendar-empty">{emptyLabel}</p></div>
  }

  const firstIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan)
  const visibleCount = Math.ceil(viewportHeight / rowHeight) + overscan * 2
  const finalIndex = Math.min(events.length, firstIndex + visibleCount)

  const trackScroll = (event: UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop)
  }

  return (
    <div className="calendar-rows" ref={viewportRef} onScroll={trackScroll}>
      <div className="calendar-rows-spacer" style={{ height: events.length * rowHeight }}>
        <div className="calendar-rows-window" style={{ transform: `translateY(${firstIndex * rowHeight}px)` }}>
          {events.slice(firstIndex, finalIndex).map((event) => {
            const countdown = countdownLabel(event.release_at, event.actual, now)
            return (
              <div
                className={`calendar-row${event.value_id === highlightedEventId ? ' highlighted-event' : ''}`}
                key={event.value_id}
              >
                <time dateTime={event.release_at ? new Date(event.release_at).toISOString() : undefined}>
                  {event.release_at ? formatAppTimestamp(event.release_at, timeDisplay, 'date-time') : '—'}
                </time>
                <span className={countdown === 'Awaiting actual' ? 'calendar-awaiting' : ''}>{countdown}</span>
                <strong>{event.currency || '—'}</strong>
                <span className={`calendar-impact ${event.importance}`}>{event.importance}</span>
                <span title={`${event.country_name} · ${event.event_code} · value ${event.value_id}`}>{event.name}</span>
                <span>{formatValue(event.actual, event)}</span>
                <span>{formatValue(event.forecast, event)}</span>
                <span>{formatValue(event.revised_previous ?? event.previous, event)}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
