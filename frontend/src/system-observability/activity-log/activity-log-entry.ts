export type ActivitySource = 'Application' | 'Appearance' | 'Chart' | 'Drawing' | 'Market Watch'

export type ActivityLogEntry = {
  id: string
  occurredAt: number
  source: ActivitySource
  action: string
  detail?: string
}
