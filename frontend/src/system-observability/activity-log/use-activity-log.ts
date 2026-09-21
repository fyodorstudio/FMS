import { useContext } from 'react'
import { ActivityLogContext } from './activity-log-context'

export function useActivityLog() {
  const context = useContext(ActivityLogContext)
  if (!context) throw new Error('useActivityLog must be used inside ActivityLogProvider')
  return context
}
