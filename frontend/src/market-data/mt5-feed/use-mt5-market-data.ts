import { useEffect, useRef, useState } from 'react'
import type { UTCTimestamp } from 'lightweight-charts'
import { BridgeRequestError, bridgeRequest } from '../../system-connectivity/bridge-status/bridge-client'
import { useActivityLog } from '../../system-observability/activity-log/use-activity-log'
import type { ChartTimeframe } from '../contracts/ChartTimeframe'
import type { OhlcBar } from '../contracts/OhlcBar'
import type { SymbolQuote } from '../contracts/SymbolQuote'

type MarketWatchResponse = {
  symbols: Array<{
    symbol: string
    description: string
    bid: number
    ask: number
    daily_change: number
    precision: number
  }>
  observed_at: number
  duration_ms: number
}

type OhlcResponse = {
  symbol: string
  timeframe: ChartTimeframe
  bars: Array<{
    time: number
    open: number
    high: number
    low: number
    close: number
    tick_volume: number
  }>
  observed_at: number
  duration_ms: number
  source_generation: number
}

export type FeedStatus = 'waiting' | 'loading' | 'live' | 'stale' | 'unavailable'

export type Mt5MarketData = {
  activeSymbol: string
  symbols: SymbolQuote[]
  bars: OhlcBar[]
  marketWatchStatus: FeedStatus
  chartStatus: FeedStatus
  marketWatchError: string | null
  chartError: string | null
  barsObservedAt: number | null
}

function barFingerprint(bars: OhlcBar[]) {
  if (bars.length === 0) return 'empty'
  return `${bars.length}:` + bars.slice(-3).map(
    (bar) => `${bar.time}:${bar.open}:${bar.high}:${bar.low}:${bar.close}`,
  ).join('|')
}

export function useMt5MarketData(
  connected: boolean,
  sourceGeneration: number,
  selectedSymbol: string,
  timeframe: ChartTimeframe,
): Mt5MarketData {
  const { appendActivity } = useActivityLog()
  const [symbols, setSymbols] = useState<SymbolQuote[]>([])
  const [bars, setBars] = useState<OhlcBar[]>([])
  const [marketWatchStatus, setMarketWatchStatus] = useState<FeedStatus>('waiting')
  const [chartStatus, setChartStatus] = useState<FeedStatus>('waiting')
  const [marketWatchError, setMarketWatchError] = useState<string | null>(null)
  const [chartError, setChartError] = useState<string | null>(null)
  const [barsObservedAt, setBarsObservedAt] = useState<number | null>(null)
  const [marketGeneration, setMarketGeneration] = useState<number | null>(null)
  const [marketAttemptGeneration, setMarketAttemptGeneration] = useState<number | null>(null)
  const [chartDataKey, setChartDataKey] = useState<string | null>(null)
  const [chartAttemptKey, setChartAttemptKey] = useState<string | null>(null)
  const marketWasLive = useRef(false)
  const chartWasLive = useRef(false)
  const marketGenerationRef = useRef<number | null>(null)
  const chartDataKeyRef = useRef<string | null>(null)
  const barsRef = useRef<OhlcBar[]>([])
  const lastFullFetchAtRef = useRef(0)
  const fingerprintRef = useRef('empty')

  useEffect(() => {
    if (!connected) return
    marketWasLive.current = false
    let disposed = false
    let timer: number | undefined
    let controller: AbortController | null = null

    const poll = async () => {
      controller = new AbortController()
      setMarketAttemptGeneration(sourceGeneration)
      setMarketWatchStatus((current) => current === 'live' ? current : 'loading')
      try {
        const response = await bridgeRequest<MarketWatchResponse>('/market-watch', controller.signal)
        if (disposed) return
        const nextSymbols = response.symbols.map((symbol) => ({
          symbol: symbol.symbol,
          description: symbol.description,
          bid: symbol.bid,
          ask: symbol.ask,
          dailyChange: symbol.daily_change,
          precision: symbol.precision,
        }))
        setSymbols(nextSymbols)
        setMarketGeneration(sourceGeneration)
        marketGenerationRef.current = sourceGeneration
        setMarketWatchStatus('live')
        setMarketWatchError(null)
        if (!marketWasLive.current) {
          appendActivity('Market Watch', 'Broker symbols loaded', `${nextSymbols.length} visible symbols`, { severity: 'success' })
        }
        marketWasLive.current = true
      } catch (error) {
        if (disposed || (error instanceof DOMException && error.name === 'AbortError')) return
        const message = error instanceof Error ? error.message : 'Market Watch request failed'
        setMarketWatchStatus(marketGenerationRef.current === sourceGeneration ? 'stale' : 'unavailable')
        setMarketWatchError(message)
        if (marketWasLive.current) {
          appendActivity('Market Watch', 'Broker symbols stale', message, { severity: 'warning' })
        }
        marketWasLive.current = false
      } finally {
        if (!disposed) timer = window.setTimeout(poll, 2_500)
      }
    }

    void poll()
    return () => {
      disposed = true
      controller?.abort()
      if (timer) window.clearTimeout(timer)
    }
  }, [appendActivity, connected, sourceGeneration])

  const symbolsAreCurrent = connected && marketGeneration === sourceGeneration
  const currentSymbols = symbolsAreCurrent ? symbols : []
  const activeSymbol = currentSymbols.some((symbol) => symbol.symbol === selectedSymbol)
    ? selectedSymbol
    : currentSymbols[0]?.symbol ?? selectedSymbol
  const requestedChartKey = `${sourceGeneration}:${activeSymbol}:${timeframe}`

  useEffect(() => {
    if (!connected || !activeSymbol) return
    let disposed = false
    let timer: number | undefined
    let controller: AbortController | null = null
    fingerprintRef.current = 'empty'
    chartWasLive.current = false
    lastFullFetchAtRef.current = 0

    const poll = async () => {
      controller = new AbortController()
      setChartAttemptKey(requestedChartKey)
      const firstLoad = chartDataKeyRef.current !== requestedChartKey
      const reconciliation = !firstLoad && Date.now() - lastFullFetchAtRef.current >= 60_000
      const requestedBarCount = firstLoad ? 5_000 : reconciliation ? 800 : 3
      try {
        const response = await bridgeRequest<OhlcResponse>(
          `/ohlc?symbol=${encodeURIComponent(activeSymbol)}&timeframe=${timeframe}&count=${requestedBarCount}`,
          controller.signal,
        )
        if (disposed || response.symbol !== activeSymbol || response.timeframe !== timeframe) return
        const receivedBars: OhlcBar[] = response.bars.map((bar) => ({
          time: bar.time as UTCTimestamp,
          open: bar.open,
          high: bar.high,
          low: bar.low,
          close: bar.close,
        }))
        const firstReceivedTime = receivedBars[0]?.time
        const nextBars = firstLoad || firstReceivedTime === undefined
          ? receivedBars
          : [...barsRef.current.filter((bar) => bar.time < firstReceivedTime), ...receivedBars]
        const fingerprint = barFingerprint(nextBars)
        if (fingerprint !== fingerprintRef.current) {
          fingerprintRef.current = fingerprint
          barsRef.current = nextBars
          setBars(nextBars)
        }
        if (firstLoad || reconciliation) lastFullFetchAtRef.current = Date.now()
        setChartDataKey(requestedChartKey)
        chartDataKeyRef.current = requestedChartKey
        setBarsObservedAt(response.observed_at)
        setChartStatus('live')
        setChartError(null)
        if (!chartWasLive.current) {
          appendActivity('Chart', 'MT5 candle history loaded', `${activeSymbol} ${timeframe} · ${nextBars.length} bars`, { severity: 'success' })
        }
        chartWasLive.current = true
      } catch (error) {
        if (disposed || (error instanceof DOMException && error.name === 'AbortError')) return
        if (error instanceof BridgeRequestError && error.code === 'superseded') return
        const message = error instanceof Error ? error.message : 'OHLC request failed'
        setChartStatus(chartDataKeyRef.current === requestedChartKey ? 'stale' : 'unavailable')
        setChartError(message)
        if (chartWasLive.current) {
          appendActivity('Chart', 'MT5 candle history stale', message, { severity: 'warning' })
        }
        chartWasLive.current = false
      } finally {
        if (!disposed) timer = window.setTimeout(poll, 2_000)
      }
    }

    void poll()
    return () => {
      disposed = true
      controller?.abort()
      if (timer) window.clearTimeout(timer)
    }
  }, [activeSymbol, appendActivity, connected, requestedChartKey, timeframe])

  const chartIsCurrent = connected && chartDataKey === requestedChartKey
  const marketFailureIsCurrent = marketAttemptGeneration === sourceGeneration && marketWatchStatus === 'unavailable'
  const chartFailureIsCurrent = chartAttemptKey === requestedChartKey && chartStatus === 'unavailable'

  return {
    activeSymbol,
    symbols: currentSymbols,
    bars: chartIsCurrent ? bars : [],
    marketWatchStatus: !connected ? 'waiting' : symbolsAreCurrent ? marketWatchStatus : marketFailureIsCurrent ? 'unavailable' : 'loading',
    chartStatus: !connected ? 'waiting' : chartIsCurrent ? chartStatus : chartFailureIsCurrent ? 'unavailable' : 'loading',
    marketWatchError: connected ? marketWatchError : null,
    chartError: chartIsCurrent || chartFailureIsCurrent ? chartError : null,
    barsObservedAt: chartIsCurrent ? barsObservedAt : null,
  }
}
