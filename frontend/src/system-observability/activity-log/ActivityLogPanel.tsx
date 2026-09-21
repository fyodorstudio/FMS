import type { ActivityLogEntry } from './activity-log-entry'
import './activity-log-panel.css'

type ActivityLogPanelProps = {
  entries: ActivityLogEntry[]
  onClear: () => void
}

function formatActivityTime(timestamp: number) {
  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(timestamp)
}

export function ActivityLogPanel({ entries, onClear }: ActivityLogPanelProps) {
  return (
    <section className="activity-panel" aria-label="Activity log">
      <header className="activity-panel-heading">
        <div>
          <strong>Activity log</strong>
          <span>Current application session · newest first</span>
        </div>
        <button type="button" onClick={onClear} disabled={entries.length === 0}>Clear</button>
      </header>

      <div className="activity-table" role="log" aria-live="polite">
        <div className="activity-table-columns" aria-hidden="true">
          <span>Time</span><span>Source</span><span>Action</span><span>Detail</span>
        </div>
        <div className="activity-table-rows">
          {[...entries].reverse().map((entry) => (
            <div className="activity-row" key={entry.id}>
              <time dateTime={new Date(entry.occurredAt).toISOString()}>{formatActivityTime(entry.occurredAt)}</time>
              <strong>{entry.source}</strong>
              <span>{entry.action}</span>
              <span>{entry.detail ?? '—'}</span>
            </div>
          ))}
          {entries.length === 0 && <p className="activity-empty">No activity recorded yet.</p>}
        </div>
      </div>
    </section>
  )
}
