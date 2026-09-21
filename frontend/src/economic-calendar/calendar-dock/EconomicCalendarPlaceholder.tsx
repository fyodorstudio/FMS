import {
  formatAppTimestamp,
  timeDisplayLabel,
  type TimeDisplayPreference,
} from '../../appearance/time-display/time-display-preference'
import './economic-calendar-placeholder.css'

const placeholderEvents = [
  { time: Date.UTC(2026, 8, 23, 8), currency: 'EUR', impact: 'Medium', event: 'Manufacturing confidence', actual: '—', forecast: '-7.1', previous: '-7.4' },
  { time: Date.UTC(2026, 8, 23, 12, 30), currency: 'GBP', impact: 'High', event: 'Consumer price index', actual: '—', forecast: '2.8%', previous: '2.6%' },
  { time: Date.UTC(2026, 8, 23, 15), currency: 'USD', impact: 'High', event: 'Consumer confidence', actual: '—', forecast: '102.4', previous: '101.8' },
  { time: Date.UTC(2026, 8, 23, 17, 30), currency: 'CAD', impact: 'Low', event: 'Wholesale sales', actual: '—', forecast: '0.3%', previous: '-0.2%' },
]

type EconomicCalendarPlaceholderProps = { timeDisplay: TimeDisplayPreference }

export function EconomicCalendarPlaceholder({ timeDisplay }: EconomicCalendarPlaceholderProps) {
  return (
    <section className="calendar-placeholder" aria-label="Economic Calendar placeholder">
      <div className="calendar-placeholder-heading">
        <div>
          <strong>Economic Calendar</strong>
          <span>Placeholder records · {timeDisplayLabel(timeDisplay)} · no MT5 source connected</span>
        </div>
        <span className="placeholder-badge">SAMPLE ONLY</span>
      </div>

      <div className="calendar-table">
        <div className="calendar-row calendar-columns" aria-hidden="true">
          <span>Time</span><span>Currency</span><span>Impact</span><span>Event</span><span>Actual</span><span>Forecast</span><span>Previous</span>
        </div>
        <div className="calendar-rows">
          {placeholderEvents.map((event) => (
            <div className="calendar-row" key={`${event.time}-${event.currency}-${event.event}`}>
              <time dateTime={new Date(event.time).toISOString()}>{formatAppTimestamp(event.time, timeDisplay, 'time-short')}</time>
              <strong>{event.currency}</strong>
              <span className={`calendar-impact ${event.impact.toLowerCase()}`}>{event.impact}</span>
              <span>{event.event}</span>
              <span>{event.actual}</span>
              <span>{event.forecast}</span>
              <span>{event.previous}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
