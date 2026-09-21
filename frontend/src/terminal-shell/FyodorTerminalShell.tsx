import { useCallback, useMemo, useState } from 'react'
import { readColorTheme, type ColorTheme } from '../appearance/color-theme/color-theme-preference'
import {
  readTimeDisplayPreference,
  saveTimeDisplayPreference,
  timeDisplayLabel,
  type TimeDisplayPreference,
} from '../appearance/time-display/time-display-preference'
import { EconomicCalendarPlaceholder } from '../economic-calendar/calendar-dock/EconomicCalendarPlaceholder'
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
import { generateSampleBars } from '../market-data/sample-feed/generate-sample-bars'
import { sampleSymbolQuotes } from '../market-data/sample-feed/sample-symbol-quotes'
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

  const quote = sampleSymbolQuotes.find((item) => item.symbol === selectedSymbol) ?? sampleSymbolQuotes[0]
  const bars = useMemo(() => generateSampleBars(quote, timeframe), [quote, timeframe])
  const fmsArrows = useMemo(
    () => createFmsPlaceholderArrows(selectedSymbol, timeframe, bars),
    [bars, selectedSymbol, timeframe],
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
    updatePositionWidth,
    clearAllDrawings,
  } = useChartDrawings(selectedSymbol, timeframe)

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
    appendActivity('Chart', 'Timeframe selected', `${selectedSymbol} ${nextTimeframe}`)
  }

  const selectLeftDockWindow = (window: LeftDockWindow) => {
    setLeftDockWindow(window)
    saveLeftDockWindow(window)
  }

  const recordChartData = useCallback(
    (barCount: number) => appendActivity('Chart', 'Candle data applied', `${selectedSymbol} ${timeframe} · ${barCount} bars`),
    [appendActivity, selectedSymbol, timeframe],
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
      appendActivity('Drawing', 'Drawing created', `${selectedSymbol} ${timeframe} · ${tool}`)
      return drawingId
    },
    [addDrawing, appendActivity, selectedSymbol, timeframe],
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

  return (
    <div className={`terminal-shell${bottomDockWindow ? ' bottom-dock-open' : ''}`}>
      <main className="terminal-workspace">
        <LeftDockPanel
          activeWindow={leftDockWindow}
          symbols={sampleSymbolQuotes}
          selectedSymbol={selectedSymbol}
          decisions={fmsPlaceholderDecisions}
          setups={fmsPlaceholderSetups}
          timeDisplay={timeDisplay}
          onSelectWindow={selectLeftDockWindow}
          onSelectSymbol={selectSymbol}
          onOpenResult={openFmsResult}
          onGoToArrow={goToPlaceholderArrow}
        />

        <section className="chart-workspace" aria-label={`${quote.symbol} chart workspace`}>
          <ChartWorkspaceHeader quote={quote} timeframe={timeframe} onSelectTimeframe={selectTimeframe} />
          <div className="chart-frame">
            <MarketCandlestickChart
              bars={bars}
              precision={quote.precision}
              theme={theme}
              appearance={chartAppearance}
              timeDisplay={timeDisplay}
              activeDrawingTool={activeDrawingTool}
              drawings={drawings}
              selectedDrawingId={selectedDrawingId}
              onSelectDrawing={setSelectedDrawingId}
              onCreateDrawing={createDrawing}
              onUpdateDrawingPoint={updateDrawingPoint}
              onUpdatePositionWidth={updatePositionWidth}
              onExitDrawingMode={() => setActiveDrawingTool(null)}
              onDataApplied={recordChartData}
              renderChartOverlay={(chartApi, seriesApi) => (
                <FmsChartMarkers
                  chartApi={chartApi}
                  seriesApi={seriesApi}
                  arrows={visibleFmsArrows}
                  onSelectArrow={openFmsResult}
                />
              )}
            />
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
              <strong>{quote.symbol}</strong>
              <span>{timeframe} · Sample data</span>
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
          {bottomDockWindow === 'activity' && <ActivityLogPanel entries={entries} timeDisplay={timeDisplay} onClear={clearActivity} />}
          {bottomDockWindow === 'calendar' && <EconomicCalendarPlaceholder timeDisplay={timeDisplay} />}
          {bottomDockWindow === 'past-result' && <FmsPastResultPanel result={selectedFmsResult} timeDisplay={timeDisplay} />}
        </BottomDockPanel>
      )}

      <TerminalStatusBar
        sourceSymbolCount={sampleSymbolQuotes.length}
        selectedSymbol={selectedSymbol}
        timeframe={timeframe}
        barCount={bars.length}
        activityCount={entries.length}
        bottomDockWindow={bottomDockWindow}
        settingsOpen={settingsOpen}
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
