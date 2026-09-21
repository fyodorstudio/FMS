import { useCallback, useMemo, useState } from 'react'
import type { ChartTimeframe } from '../contracts/ChartTimeframe'
import type { ChartDrawingPoint, ChartDrawingRecord } from './chart-drawing-record'
import { readChartDrawings, saveChartDrawings } from './chart-drawing-storage'
import type { DrawingToolId } from './drawing-tool'

export function useChartDrawings(symbol: string, timeframe: ChartTimeframe) {
  const [allDrawings, setAllDrawings] = useState<ChartDrawingRecord[]>(readChartDrawings)
  const drawings = useMemo(
    () => allDrawings.filter((drawing) => drawing.symbol === symbol && drawing.timeframe === timeframe),
    [allDrawings, symbol, timeframe],
  )

  const addDrawing = useCallback(
    (tool: DrawingToolId, points: ChartDrawingPoint[]) => {
      const nextDrawing: ChartDrawingRecord = {
        id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
        symbol,
        timeframe,
        tool,
        points,
        createdAt: Date.now(),
      }
      setAllDrawings((current) => {
        const next = [...current, nextDrawing]
        saveChartDrawings(next)
        return next
      })
    },
    [symbol, timeframe],
  )

  const updateDrawingPoint = useCallback((drawingId: string, pointIndex: number, point: ChartDrawingPoint, persist: boolean) => {
    setAllDrawings((current) => {
      const next = current.map((drawing) => {
        if (drawing.id !== drawingId || !drawing.points[pointIndex]) return drawing
        const points = [...drawing.points]
        points[pointIndex] = point

        if ((drawing.tool === 'long-position' || drawing.tool === 'short-position') && points.length >= 3) {
          if (pointIndex === 1) points[2] = { ...points[2], time: point.time }
          if (pointIndex === 2) points[1] = { ...points[1], time: point.time }
        }

        return { ...drawing, points }
      })
      if (persist) saveChartDrawings(next)
      return next
    })
  }, [])

  const updatePositionWidth = useCallback((drawingId: string, time: ChartDrawingPoint['time'], persist: boolean) => {
    setAllDrawings((current) => {
      const next = current.map((drawing) => {
        if (
          drawing.id !== drawingId ||
          (drawing.tool !== 'long-position' && drawing.tool !== 'short-position') ||
          drawing.points.length < 3
        ) return drawing
        const points = [...drawing.points]
        points[1] = { ...points[1], time }
        points[2] = { ...points[2], time }
        return { ...drawing, points }
      })
      if (persist) saveChartDrawings(next)
      return next
    })
  }, [])

  const clearAllDrawings = useCallback(() => {
    setAllDrawings([])
    saveChartDrawings([])
  }, [])

  return {
    drawings,
    totalDrawingCount: allDrawings.length,
    addDrawing,
    updateDrawingPoint,
    updatePositionWidth,
    clearAllDrawings,
  }
}
