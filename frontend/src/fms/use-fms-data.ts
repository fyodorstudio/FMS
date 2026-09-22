import { useEffect, useState } from 'react'
import type {
  FmsEngineStatus,
  FmsPortfolioSummary,
  FmsRegisteredSetupDTO,
  FmsSignalDTO,
} from './contracts/fms-api-types'
import {
  fetchFmsHealth,
  fetchFmsSetups,
  fetchFmsSignals,
  fetchFmsSummary,
} from './fms-client'

export type FmsDataState = {
  setups: FmsRegisteredSetupDTO[]
  summary: FmsPortfolioSummary | null
  signals: FmsSignalDTO[]
  engineStatus: FmsEngineStatus | null
  isOnline: boolean
  loading: boolean
  error: string | null
  refresh: () => void
}

export function useFmsData(activeSymbol: string): FmsDataState {
  const [setups, setSetups] = useState<FmsRegisteredSetupDTO[]>([])
  const [summary, setSummary] = useState<FmsPortfolioSummary | null>(null)
  const [signals, setSignals] = useState<FmsSignalDTO[]>([])
  const [engineStatus, setEngineStatus] = useState<FmsEngineStatus | null>(null)
  const [isOnline, setIsOnline] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  // 1. Fetch Health, Setups, and Summary
  useEffect(() => {
    let disposed = false
    const abortController = new AbortController()

    const loadGlobalFms = async () => {
      setLoading(true)
      try {
        const [health, setupsList, summaryData] = await Promise.all([
          fetchFmsHealth(abortController.signal),
          fetchFmsSetups(abortController.signal),
          fetchFmsSummary(abortController.signal),
        ])

        if (!disposed) {
          setEngineStatus(health)
          setIsOnline(health.status === 'operational')
          setSetups(setupsList)
          setSummary(summaryData)
          setError(null)
        }
      } catch (err) {
        if (!disposed) {
          setIsOnline(false)
          setError((err as Error).message || 'FMS engine unreachable')
        }
      } finally {
        if (!disposed) {
          setLoading(false)
        }
      }
    }

    loadGlobalFms()

    // Poll health periodically every 20s
    const timer = window.setInterval(loadGlobalFms, 20_000)

    return () => {
      disposed = true
      abortController.abort()
      window.clearInterval(timer)
    }
  }, [refreshTrigger])

  // 2. Fetch Signals for activeSymbol
  useEffect(() => {
    let disposed = false
    const abortController = new AbortController()

    const loadSignals = async () => {
      if (!activeSymbol) return
      try {
        const sigs = await fetchFmsSignals(activeSymbol, abortController.signal)
        if (!disposed) {
          setSignals(sigs)
        }
      } catch {
        if (!disposed) {
          setSignals([])
        }
      }
    }

    loadSignals()

    return () => {
      disposed = true
      abortController.abort()
    }
  }, [activeSymbol, refreshTrigger])

  return {
    setups,
    summary,
    signals,
    engineStatus,
    isOnline,
    loading,
    error,
    refresh: () => setRefreshTrigger((prev) => prev + 1),
  }
}
