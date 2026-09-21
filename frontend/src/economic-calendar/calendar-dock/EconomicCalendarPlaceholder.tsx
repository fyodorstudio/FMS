import './economic-calendar-placeholder.css'

const placeholderEvents = [
  { time: '08:00', currency: 'EUR', impact: 'Medium', event: 'Manufacturing confidence', actual: '—', forecast: '-7.1', previous: '-7.4' },
  { time: '12:30', currency: 'GBP', impact: 'High', event: 'Consumer price index', actual: '—', forecast: '2.8%', previous: '2.6%' },
  { time: '15:00', currency: 'USD', impact: 'High', event: 'Consumer confidence', actual: '—', forecast: '102.4', previous: '101.8' },
  { time: '17:30', currency: 'CAD', impact: 'Low', event: 'Wholesale sales', actual: '—', forecast: '0.3%', previous: '-0.2%' },
]

export function EconomicCalendarPlaceholder() {
  return (
    <section className="calendar-placeholder" aria-label="Economic Calendar placeholder">
      <div className="calendar-placeholder-heading">
        <div>
          <strong>Economic Calendar</strong>
          <span>Placeholder records · no MT5 source connected</span>
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
              <time>{event.time}</time>
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
