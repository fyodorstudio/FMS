export type BridgeOperation = {
  state: 'idle' | 'running' | 'failed'
  operation: string | null
  operation_started_at: number | null
  last_success_at: number | null
  last_duration_ms: number | null
  last_error: string | null
  count: number | null
}

export type BridgeHealth = {
  api_version: string
  bridge: {
    status: 'running'
    version: string
    started_at: number
    now: number
    uptime_ms: number
  }
  mt5: {
    process_running: boolean
    process_id: number | null
    terminal_path: string | null
    connected: boolean
    state: string
    generation: number
    last_attempt_at: number | null
    last_success_at: number | null
    last_error: string | null
    package_version: string | null
    account_login: number | null
    account_server: string | null
  }
  calendar: CalendarSourceHealth
  operations: Record<string, BridgeOperation>
}

export type CalendarSourceHealth = {
  status: 'waiting-for-publisher' | 'awaiting-snapshot' | 'live' | 'stale'
  instance_id: string | null
  last_heartbeat_at: number | null
  last_snapshot_at: number | null
  last_update_at: number | null
  server_time_seconds: number | null
  server_utc_offset_seconds: number | null
  change_id: string | null
  publisher_request_duration_ms: number | null
  clock_trust: 'unavailable' | 'observed'
  event_count: number
}

export type BridgeActivityEvent = {
  sequence: number
  occurred_at: number
  source: string
  severity: 'info' | 'success' | 'warning' | 'error'
  action: string
  detail: string | null
}
