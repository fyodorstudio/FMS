import { useCallback, useMemo, useState } from 'react'
import { readColorTheme, type ColorTheme } from '../appearance/color-theme/color-theme-preference'
import {
  readTimeDisplayPreference,
  saveTimeDisplayPreference,
  timeDisplayLabel,
  type TimeDisplayPreference,
} from '../appearance/time-display/time-display-preference'
import { EconomicCalendarMarkers } from '../economic-calendar/calendar-dock/EconomicCalendarMarkers'
import { EconomicCalendarPanel } from '../economic-calendar/calendar-dock/EconomicCalendarPanel'
import type { CalendarRangePreset } from '../economic-calendar/calendar-dock/calendar-display-range'
import { useMt5EconomicCalendar } from '../economic-calendar/mt5-calendar/use-mt5-economic-calendar'
import { FmsArrowControls } from '../fms/chart-arrows/FmsArrowControls'
import { FmsChartMarkers } from '../fms/chart-arrows/FmsChartMarkers'
import { FmsPastResultPanel } from '../fms/past-result-dock/FmsPastResultPanel'
import {
  createFmsPlaceholderArrows,
  fmsPlaceholderDecisions,
  fmsPlaceholderSetups,
} from '../fms/placeholder-feed/fms-placeholder-data'
import type {
  FmsArrowFilter,
  FmsChartArrow,
  FmsDecision,
} from '../fms/placeholder-feed/fms-placeholder-types'
import { MarketCandlestickChart } from '../market-data/candlestick-chart/MarketCandlestickChart'
import { MarketChartErrorBoundary } from '../market-data/candlestick-chart/MarketChartErrorBoundary'
import { FloatingDrawingToolbar } from '../market-data/chart-drawings/FloatingDrawingToolbar'
import type { ChartDrawingPoint } from '../market-data/chart-drawings/chart-drawing-record'
import type { DrawingToolId } from '../market-data/chart-drawings/drawing-tool'
import { useChartDrawings } from '../market-data/chart-drawings/use-chart-drawings'
import { ChartSettingsPopover } from '../market-data/chart-settings/ChartSettingsPopover'
import {
  readChartAppearance,
  saveChartAppearance,
  type ChartAppearance,
} from '../market-data/chart-settings/chart-appearance-preference'
import type { ChartTimeframe } from '../market-data/contracts/ChartTimeframe'
import { CandleHistoryLoadingNotice, MarketDataNotice } from '../market-data/mt5-feed/MarketDataNotice'
import { useMt5MarketData } from '../market-data/mt5-feed/use-mt5-market-data'
import { DataHeartbeatPanel } from '../system-connectivity/bridge-status/DataHeartbeatPanel'
import { useBridgeStatus } from '../system-connectivity/bridge-status/use-bridge-status'
import { ActivityLogPanel } from '../system-observability/activity-log/ActivityLogPanel'
import { useActivityLog } from '../system-observability/activity-log/use-activity-log'
import { BottomDockPanel } from '../workspace-docking/bottom-dock/BottomDockPanel'
import type { BottomDockWindow } from '../workspace-docking/bottom-dock/bottom-dock-window'
import { LeftDockPanel } from '../workspace-docking/left-dock/LeftDockPanel'
import {
  readLeftDockWindow,
  saveLeftDockWindow,
  type LeftDockWindow,
} from '../workspace-docking/left-dock/left-dock-window'
import { ChartWorkspaceHeader } from './ChartWorkspaceHeader'
import { TerminalStatusBar } from './TerminalStatusBar'
import './terminal-shell.layout.css'

type SelectedFmsResult = FmsChartArrow | FmsDecision

export function FyodorTerminalShell() {
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD')
  const [timeframe, setTimeframe] = useState<ChartTimeframe>('H4')
  const [theme, setTheme] = useState<ColorTheme>(readColorTheme)
  const [chartAppearance, setChartAppearance] = useState<ChartAppearance>(readChartAppearance)
  const [timeDisplay, setTimeDisplay] = useState<TimeDisplayPreference>(readTimeDisplayPreference)
  const [activeDrawingTool, setActiveDrawingTool] = useState<DrawingToolId | null>(null)
  const [selectedDrawingId, setSelectedDrawingId] = useState<string | null>(null)
  const [bottomDockWindow, setBottomDockWindow] = useState<BottomDockWindow | null>(null)
  const [leftDockWindow, setLeftDockWindow] = useState<LeftDockWindow>(readLeftDockWindow)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [pastArrowsVisible, setPastArrowsVisible] = useState(true)
  const [arrowFilter, setArrowFilter] = useState<FmsArrowFilter>('all')
  const [selectedFmsResult, setSelectedFmsResult] = useState<SelectedFmsResult | null>(null)
  const { entries, appendActivity, clearActivity } = useActivityLog()
  const bridge = useBridgeStatus()
  const mt5Connected = bridge.health?.mt5.connected === true
  const marketData = useMt5MarketData(mt5Connected, bridge.health?.mt5.generation ?? 0, selectedSymbol, timeframe)
  const calendar = useMt5EconomicCalendar(
    bridge.reachable,
    bridge.health?.calendar ?? null,
    bottomDockWindow === 'calendar',
  )
  const activeSymbol = marketData.activeSymbol
  const quote = marketData.symbols.find((item) => item.symbol === activeSymbol) ?? null
  const bars = marketData.bars

  const fmsArrows = useMemo(
    () => createFmsPlaceholderArrows(activeSymbol, timeframe, bars),
    [activeSymbol, bars, timeframe],
  )
  const visibleFmsArrows = useMemo(() => {
    if (!pastArrowsVisible) return []
    return fmsArrows.filter((arrow) => {
      if (arrowFilter === 'wins') return arrow.result === 'tp-reached'
      if (arrowFilter === 'losses') return arrow.result === 'sl-reached'
      if (arrowFilter === 'v1' || arrowFilter === 'v2') return arrow.version === arrowFilter
      return true
    })
  }, [arrowFilter, fmsArrows, pastArrowsVisible])

  const {
    drawings,
    totalDrawingCount,
    addDrawing,
    updateDrawingPoint,
    updateDrawingPoints,
    updateDrawingText,
    updatePositionWidth,
    deleteDrawing,
    clearAllDrawings,
  } = useChartDrawings(activeSymbol, timeframe)

  const [highlightedCalendarEventId, setHighlightedCalendarEventId] = useState<string | null>(null)
  const [calendarRangePreset, setCalendarRangePreset] = useState<CalendarRangePreset>('this-week')

  const handleDeleteDrawing = useCallback((drawingId: string) => {
    deleteDrawing(drawingId)
    if (selectedDrawingId === drawingId) setSelectedDrawingId(null)
    appendActivity('Drawing', 'Drawing deleted', `${activeSymbol} ${timeframe}`)
  }, [activeSymbol, appendActivity, deleteDrawing, selectedDrawingId, timeframe])

  const selectSymbol = (symbol: string) => {
    if (symbol === selectedSymbol) return
    setSelectedSymbol(symbol)
    setSelectedDrawingId(null)
    appendActivity('Market Watch', 'Symbol selected', symbol)
  }

  const selectTimeframe = (nextTimeframe: ChartTimeframe) => {
    if (nextTimeframe === timeframe) return
    setTimeframe(nextTimeframe)
    setSelectedDrawingId(null)
    appendActivity('Chart', 'Timeframe selected', `${activeSymbol} ${nextTimeframe}`)
  }

  const selectLeftDockWindow = (window: LeftDockWindow) => {
    setLeftDockWindow(window)
    saveLeftDockWindow(window)
  }

  const recordChartData = useCallback(
    (barCount: number) => appendActivity('Chart', 'Candle data applied', `${activeSymbol} ${timeframe} · ${barCount} bars`),
    [activeSymbol, appendActivity, timeframe],
  )

  const changeTheme = (nextTheme: ColorTheme) => {
    setTheme(nextTheme)
    appendActivity('Appearance', 'Theme changed', nextTheme === 'light' ? 'Light' : 'Dark')
  }

  const changeChartAppearance = (nextAppearance: ChartAppearance) => {
    setChartAppearance(nextAppearance)
    saveChartAppearance(nextAppearance)
  }

  const changeTimeDisplay = (nextPreference: TimeDisplayPreference) => {
    setTimeDisplay(nextPreference)
    saveTimeDisplayPreference(nextPreference)
    appendActivity('Appearance', 'Time display changed', timeDisplayLabel(nextPreference))
  }

  const createDrawing = useCallback(
    (tool: DrawingToolId, points: ChartDrawingPoint[]) => {
      const drawingId = addDrawing(tool, points)
      appendActivity('Drawing', 'Drawing created', `${activeSymbol} ${timeframe} · ${tool}`)
      return drawingId
    },
    [activeSymbol, addDrawing, appendActivity, timeframe],
  )

  const chooseDrawingTool = (tool: DrawingToolId | null) => {
    setActiveDrawingTool(tool)
    setSelectedDrawingId(null)
  }

  const selectCrosshair = () => {
    setActiveDrawingTool(null)
    setSelectedDrawingId(null)
  }

  const deleteAllDrawings = () => {
    clearAllDrawings()
    setSelectedDrawingId(null)
    appendActivity('Drawing', 'All drawings deleted', `${totalDrawingCount} removed`)
  }

  const openFmsResult = (result: SelectedFmsResult) => {
    setSelectedFmsResult(result)
    setBottomDockWindow('past-result')
  }

  const goToPlaceholderArrow = (decision: FmsDecision) => {
    selectSymbol(decision.symbol)
    setPastArrowsVisible(true)
    setArrowFilter(decision.version)
    openFmsResult(decision)
  }

  const toggleBottomDock = (window: BottomDockWindow) => {
    setBottomDockWindow((current) => current === window ? null : window)
  }

  const sourceState = !bridge.reachable || marketData.marketWatchStatus === 'unavailable'
    ? 'error'
    : mt5Connected && marketData.marketWatchStatus === 'live'
      ? 'live'
      : 'waiting'
  const sourceLabel = !bridge.reachable
    ? 'Bridge unreachable'
    : mt5Connected
      ? 'MT5 broker source'
      : bridge.health?.mt5.process_running
        ? 'MT5 disconnected'
        : 'Waiting for MT5'
  const calendarStatus = bridge.reachable
    ? calendar.source?.status ?? bridge.health?.calendar.status ?? 'waiting'
    : 'unavailable'

  return (
    <div className={`terminal-shell${bottomDockWindow ? ' bottom-dock-open' : ''}`}>
      <main className="terminal-workspace">
        <LeftDockPanel
          activeWindow={leftDockWindow}
          symbols={marketData.symbols}
          selectedSymbol={activeSymbol}
          marketWatchStatus={marketData.marketWatchStatus}
          marketWatchError={marketData.marketWatchError}
          decisions={fmsPlaceholderDecisions}
          setups={fmsPlaceholderSetups}
          timeDisplay={timeDisplay}
          onSelectWindow={selectLeftDockWindow}
          onSelectSymbol={selectSymbol}
          onOpenResult={openFmsResult}
          onGoToArrow={goToPlaceholderArrow}
        />

        <section className="chart-workspace" aria-label={`${activeSymbol} chart workspace`}>
          <ChartWorkspaceHeader symbol={activeSymbol} quote={quote} timeframe={timeframe} onSelectTimeframe={selectTimeframe} />
          <div className="chart-frame">
            <MarketChartErrorBoundary
              symbol={activeSymbol}
              timeframe={timeframe}
              onError={(error) => appendActivity('Chart', 'Chart error caught', error.message, { severity: 'error' })}
            >
              <MarketCandlestickChart
                bars={bars}
                fitContentKey={`${activeSymbol}:${timeframe}`}
                precision={quote?.precision ?? 5}
                theme={theme}
                appearance={chartAppearance}
                timeDisplay={timeDisplay}
                timeframe={timeframe}
                activeDrawingTool={activeDrawingTool}
                drawings={drawings}
                selectedDrawingId={selectedDrawingId}
                onSelectDrawing={setSelectedDrawingId}
                onCreateDrawing={createDrawing}
                onUpdateDrawingPoint={updateDrawingPoint}
                onUpdateDrawingPoints={updateDrawingPoints}
                onUpdatePositionWidth={updatePositionWidth}
                onUpdateDrawingText={updateDrawingText}
                onDeleteDrawing={handleDeleteDrawing}
                onExitDrawingMode={() => setActiveDrawingTool(null)}
                onDataApplied={recordChartData}
                hasOlderData={!marketData.chartHistoryComplete}
                isLoadingOlderData={marketData.chartHistoryLoading}
                onRequestOlderData={marketData.requestOlderBars}
                renderChartOverlay={(chartApi, seriesApi) => (
                  <>
                    <FmsChartMarkers
                      chartApi={chartApi}
                      seriesApi={seriesApi}
                      arrows={visibleFmsArrows}
                      onSelectArrow={openFmsResult}
                    />
                    <EconomicCalendarMarkers
                      chartApi={chartApi}
                      seriesApi={seriesApi}
                      symbol={activeSymbol}
                      bars={bars}
                      events={calendar.events}
                      rangePreset={calendarRangePreset}
                      timeDisplay={timeDisplay}
                      clockOffsetMs={bridge.clockOffsetMs}
                      onSelectEvent={(event) => {
                        setBottomDockWindow('calendar')
                        setHighlightedCalendarEventId(event.value_id)
                      }}
                    />
                  </>
                )}
              />
            </MarketChartErrorBoundary>
            <MarketDataNotice status={marketData.chartStatus} symbol={activeSymbol} timeframe={timeframe} error={marketData.chartError} />
            {marketData.chartStatus === 'live' && marketData.chartHistoryLoading && (
              <CandleHistoryLoadingNotice symbol={activeSymbol} timeframe={timeframe} />
            )}
            <FloatingDrawingToolbar
              activeTool={activeDrawingTool}
              drawingCount={totalDrawingCount}
              onSelectCrosshair={selectCrosshair}
              onToolChange={chooseDrawingTool}
              onClearAll={deleteAllDrawings}
            />
            <FmsArrowControls
              visible={pastArrowsVisible}
              filter={arrowFilter}
              arrowCount={visibleFmsArrows.length}
              onVisibleChange={setPastArrowsVisible}
              onFilterChange={setArrowFilter}
            />
            <div className="chart-watermark" aria-hidden="true">
              <strong>{activeSymbol}</strong>
              <span>
                {timeframe} · {marketData.chartStatus === 'live' ? 'MT5 broker data' : 'Awaiting MT5 data'}
                {marketData.chartHistoryComplete ? ' · beginning of MT5 history reached' : ''}
              </span>
            </div>
          </div>
        </section>
      </main>

      {bottomDockWindow && (
        <BottomDockPanel
          activeWindow={bottomDockWindow}
          activityCount={entries.length}
          hasPastResult={selectedFmsResult !== null}
          onSelectWindow={setBottomDockWindow}
          onClose={() => setBottomDockWindow(null)}
        >
          {bottomDockWindow === 'activity' && (
            <ActivityLogPanel
              entries={entries}
              timeDisplay={timeDisplay}
              onClear={clearActivity}
              heartbeat={(
                <DataHeartbeatPanel
                  health={bridge.health}
                  reachable={bridge.reachable}
                  lastContactAt={bridge.lastContactAt}
                  roundTripMs={bridge.roundTripMs}
                  probeStartedAt={bridge.probeStartedAt}
                />
              )}
            />
          )}
          {bottomDockWindow === 'calendar' && (
            <EconomicCalendarPanel
              events={calendar.events}
              source={calendar.source}
              error={calendar.error}
              clockOffsetMs={bridge.clockOffsetMs}
              timeDisplay={timeDisplay}
              highlightedEventId={highlightedCalendarEventId}
              rangePreset={calendarRangePreset}
              onRangePresetChange={setCalendarRangePreset}
            />
          )}
          {bottomDockWindow === 'past-result' && <FmsPastResultPanel result={selectedFmsResult} timeDisplay={timeDisplay} />}
        </BottomDockPanel>
      )}

      <TerminalStatusBar
        sourceState={sourceState}
        sourceLabel={sourceLabel}
        sourceSymbolCount={marketData.symbols.length}
        selectedSymbol={activeSymbol}
        timeframe={timeframe}
        barCount={bars.length}
        activityCount={entries.length}
        bottomDockWindow={bottomDockWindow}
        settingsOpen={settingsOpen}
        calendarStatus={calendarStatus}
        calendarEventCount={bridge.health?.calendar.event_count ?? 0}
        onToggleBottomDock={toggleBottomDock}
        onThemeChanged={changeTheme}
        onToggleSettings={() => setSettingsOpen((open) => !open)}
      />

      {settingsOpen && (
        <ChartSettingsPopover
          appearance={chartAppearance}
          timeDisplay={timeDisplay}
          onChange={changeChartAppearance}
          onTimeDisplayChange={changeTimeDisplay}
          onClose={() => setSettingsOpen(false)}
        />
      )}
    </div>
  )
}
