import { useEffect, useMemo, useState } from 'react'
import {
  formatAppTimestamp,
  timeDisplayLabel,
  type TimeDisplayPreference,
} from '../../appearance/time-display/time-display-preference'
import type { CalendarSourceHealth } from '../../system-connectivity/bridge-status/bridge-contract'
import type { EconomicCalendarEvent } from '../mt5-calendar/calendar-contract'
import './economic-calendar-panel.css'

type EconomicCalendarPanelProps = {
  events: EconomicCalendarEvent[]
  source: CalendarSourceHealth | null
  error: string | null
  clockOffsetMs: number
  timeDisplay: TimeDisplayPreference
}

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

const multiplierSuffix: Record<number, string> = { 1: 'K', 2: 'M', 3: 'B', 4: 'T' }

function formatValue(value: number | null, event: EconomicCalendarEvent) {
  if (value === null) return '—'
  const number = value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: Math.min(event.digits, 6),
  })
  if (event.unit === 1) return `${number}%`
  return `${number}${multiplierSuffix[event.multiplier] ?? ''}`
}

function sourceLabel(source: CalendarSourceHealth | null, error: string | null) {
  if (error) return error
  if (!source) return 'Waiting for the local bridge'
  if (source.status === 'live') return `${source.event_count} MT5 events · live publisher`
  if (source.status === 'awaiting-snapshot') return 'Calendar EA connected · receiving atomic snapshot'
  if (source.status === 'stale') return 'Calendar EA heartbeat is stale'
  return 'Attach FyodorCalendarPublisher to one MT5 chart'
}

export function EconomicCalendarPanel({ events, source, error, clockOffsetMs, timeDisplay }: EconomicCalendarPanelProps) {
  const [now, setNow] = useState(() => Date.now() + clockOffsetMs)
  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now() + clockOffsetMs), 1_000)
    return () => window.clearInterval(timer)
  }, [clockOffsetMs])
  const orderedEvents = useMemo(
    () => [...events].sort((left, right) => (left.release_at ?? Number.MAX_SAFE_INTEGER) - (right.release_at ?? Number.MAX_SAFE_INTEGER)),
    [events],
  )

  return (
    <section className="economic-calendar" aria-label="Economic Calendar">
      <div className="economic-calendar-heading">
        <div>
          <strong>Economic Calendar</strong>
          <span>{sourceLabel(source, error)} · {timeDisplayLabel(timeDisplay)}</span>
        </div>
        <span className={`calendar-source-badge ${source?.status ?? 'waiting-for-publisher'}`}>
          {source?.status === 'live' ? 'MT5 LIVE' : source?.status.replaceAll('-', ' ').toUpperCase() ?? 'WAITING'}
        </span>
      </div>

      <div className="calendar-table">
        <div className="calendar-row calendar-columns" aria-hidden="true">
          <span>Time</span><span>Countdown</span><span>Currency</span><span>Importance</span><span>Event</span><span>Actual</span><span>Forecast</span><span>Previous</span>
        </div>
        <div className="calendar-rows">
          {orderedEvents.map((event) => {
            const countdown = countdownLabel(event.release_at, event.actual, now)
            return (
              <div className="calendar-row" key={event.value_id}>
                <time dateTime={event.release_at ? new Date(event.release_at).toISOString() : undefined}>
                  {event.release_at ? formatAppTimestamp(event.release_at, timeDisplay, 'date-time') : '—'}
                </time>
                <span className={countdown === 'Awaiting actual' ? 'calendar-awaiting' : ''}>{countdown}</span>
                <strong>{event.currency || '—'}</strong>
                <span className={`calendar-impact ${event.importance}`}>{event.importance}</span>
                <span title={`${event.country_name} · ${event.event_code}`}>{event.name}</span>
                <span>{formatValue(event.actual, event)}</span>
                <span>{formatValue(event.forecast, event)}</span>
                <span>{formatValue(event.revised_previous ?? event.previous, event)}</span>
              </div>
            )
          })}
          {orderedEvents.length === 0 && (
            <p className="calendar-empty">{sourceLabel(source, error)}</p>
          )}
        </div>
      </div>
    </section>
  )
}
