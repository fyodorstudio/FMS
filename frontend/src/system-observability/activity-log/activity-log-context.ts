import { createContext } from 'react'
import type { ActivityLogEntry, ActivitySource } from './activity-log-entry'

export type ActivityLogState = {
  entries: ActivityLogEntry[]
  appendActivity: (source: ActivitySource, action: string, detail?: string) => void
  clearActivity: () => void
}

export const ActivityLogContext = createContext<ActivityLogState | null>(null)
