import { activitySources, type ActivitySource } from './activity-log-entry'

const storageKey = 'fyodor.activity-visible-sources.v2'

export function readVisibleActivitySources() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(storageKey) ?? 'null') as unknown
    if (!Array.isArray(parsed)) return new Set<ActivitySource>(activitySources)
    const valid = parsed.filter((source): source is ActivitySource => activitySources.includes(source as ActivitySource))
    return new Set<ActivitySource>(valid)
  } catch {
    return new Set<ActivitySource>(activitySources)
  }
}

export function saveVisibleActivitySources(sources: Set<ActivitySource>) {
  try {
    window.localStorage.setItem(storageKey, JSON.stringify([...sources]))
  } catch {
    // The current-session source filter still works when storage is unavailable.
  }
}
