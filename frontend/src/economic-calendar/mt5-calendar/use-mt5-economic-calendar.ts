import { useEffect, useRef, useState } from 'react'
import { bridgeRequest } from '../../system-connectivity/bridge-status/bridge-client'
import { useActivityLog } from '../../system-observability/activity-log/use-activity-log'
import type { CalendarSourceHealth } from '../../system-connectivity/bridge-status/bridge-contract'
import type { EconomicCalendarEvent, EconomicCalendarResponse } from './calendar-contract'

export type Mt5EconomicCalendar = {
  events: EconomicCalendarEvent[]
  source: CalendarSourceHealth | null
  error: string | null
}

export function useMt5EconomicCalendar(reachable: boolean): Mt5EconomicCalendar {
  const { appendActivity } = useActivityLog()
  const [events, setEvents] = useState<EconomicCalendarEvent[]>([])
  const [source, setSource] = useState<CalendarSourceHealth | null>(null)
  const [error, setError] = useState<string | null>(null)
  const wasLive = useRef(false)

  useEffect(() => {
    if (!reachable) return
    wasLive.current = false
    let disposed = false
    let timer: number | undefined
    let controller: AbortController | null = null

    const poll = async () => {
      controller = new AbortController()
      try {
        const response = await bridgeRequest<EconomicCalendarResponse>('/calendar', controller.signal)
        if (disposed) return
        setEvents(response.events)
        setSource(response.source)
        setError(null)
        if (response.source.status === 'live' && !wasLive.current) {
          appendActivity('Calendar', 'Calendar feed live', `${response.events.length} MT5 events`, { severity: 'success' })
        }
        if (response.source.status === 'stale' && wasLive.current) {
          appendActivity('Calendar', 'Calendar publisher stale', 'No publisher heartbeat for more than 30 seconds', { severity: 'warning' })
        }
        wasLive.current = response.source.status === 'live'
      } catch (requestError) {
        if (disposed || (requestError instanceof DOMException && requestError.name === 'AbortError')) return
        setError(requestError instanceof Error ? requestError.message : 'Calendar request failed')
        wasLive.current = false
      } finally {
        if (!disposed) timer = window.setTimeout(poll, 2_000)
      }
    }

    void poll()
    return () => {
      disposed = true
      controller?.abort()
      if (timer) window.clearTimeout(timer)
    }
  }, [appendActivity, reachable])

  return reachable ? { events, source, error } : { events: [], source: null, error: null }
}
