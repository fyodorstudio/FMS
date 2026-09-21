export type ActivitySource =
  | 'Application'
  | 'Appearance'
  | 'Bridge'
  | 'Calendar'
  | 'Chart'
  | 'Drawing'
  | 'Market Watch'
  | 'MT5'

export const activitySources: ActivitySource[] = [
  'Application',
  'Bridge',
  'MT5',
  'Calendar',
  'Market Watch',
  'Chart',
  'Drawing',
  'Appearance',
]

export type ActivitySeverity = 'info' | 'success' | 'warning' | 'error'

export type ActivityLogEntry = {
  id: string
  occurredAt: number
  source: ActivitySource
  action: string
  detail?: string
  severity?: ActivitySeverity
}
