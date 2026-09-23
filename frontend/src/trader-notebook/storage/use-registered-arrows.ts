import { useCallback, useEffect, useMemo, useState } from 'react'
import type { RegisteredTradeArrow } from '../contracts/trader-notebook-types'

const storageKey = 'fyodor.registered_arrows.v1'

function loadSavedArrows(): RegisteredTradeArrow[] {
  try {
    const raw = localStorage.getItem(storageKey)
    if (!raw) return []
    return JSON.parse(raw) as RegisteredTradeArrow[]
  } catch {
    return []
  }
}

function persistArrows(arrows: RegisteredTradeArrow[]) {
  try {
    localStorage.setItem(storageKey, JSON.stringify(arrows))
  } catch {
    // quota exceeded or private mode
  }
}

export function useRegisteredArrows(symbol: string) {
  const [allArrows, setAllArrows] = useState<RegisteredTradeArrow[]>(loadSavedArrows)
  const [selectedArrowId, setSelectedArrowId] = useState<string | null>(null)

  // Listen to cross-tab storage changes
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === storageKey && e.newValue) {
        try {
          setAllArrows(JSON.parse(e.newValue) as RegisteredTradeArrow[])
        } catch {
          // ignore
        }
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  const symbolArrows = useMemo(() => {
    return allArrows.filter((a) => a.symbol === symbol)
  }, [allArrows, symbol])

  const selectedArrow = useMemo(() => {
    if (!selectedArrowId) return null
    return allArrows.find((a) => a.id === selectedArrowId) ?? null
  }, [allArrows, selectedArrowId])

  const addArrow = useCallback((data: Omit<RegisteredTradeArrow, 'id' | 'createdAt'>) => {
    const newArrow: RegisteredTradeArrow = {
      ...data,
      id: `arrow_${data.symbol}_${Date.now()}`,
      createdAt: Date.now(),
    }
    setAllArrows((prev) => {
      const updated = [newArrow, ...prev]
      persistArrows(updated)
      return updated
    })
    setSelectedArrowId(newArrow.id)
    return newArrow
  }, [])

  const deleteArrow = useCallback((id: string) => {
    setAllArrows((prev) => {
      const updated = prev.filter((a) => a.id !== id)
      persistArrows(updated)
      return updated
    })
    setSelectedArrowId((curr) => (curr === id ? null : curr))
  }, [])

  return {
    allArrows,
    symbolArrows,
    selectedArrowId,
    selectedArrow,
    setSelectedArrowId,
    addArrow,
    deleteArrow,
  }
}
