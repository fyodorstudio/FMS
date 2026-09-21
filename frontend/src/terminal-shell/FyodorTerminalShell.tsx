import { useCallback, useMemo, useState } from 'react'
import { ColorThemeButton } from '../appearance/color-theme/ColorThemeButton'
import { readColorTheme, type ColorTheme } from '../appearance/color-theme/color-theme-preference'
import { EconomicCalendarPlaceholder } from '../economic-calendar/calendar-dock/EconomicCalendarPlaceholder'
import { FmsArrowControls } from '../fms/chart-arrows/FmsArrowControls'
import { FmsChartArrowOverlay } from '../fms/chart-arrows/FmsChartArrowOverlay'
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
import { normalizeDrawingPoints } from '../market-data/chart-drawings/position-drawing-geometry'
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
import './terminal-shell.layout.css'

type SelectedFmsResult = FmsChartArrow | FmsDecision

export function FyodorTerminalShell() {
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD')
  const [timeframe, setTimeframe] = useState<ChartTimeframe>('H4')
  const [theme, setTheme] = useState<ColorTheme>(readColorTheme)
  const [chartAppearance, setChartAppearance] = useState<ChartAppearance>(readChartAppearance)
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

  const createDrawing = useCallback(
    (tool: DrawingToolId, points: ChartDrawingPoint[]) => {
      addDrawing(tool, normalizeDrawingPoints(tool, points))
      appendActivity('Drawing', 'Drawing created', `${selectedSymbol} ${timeframe} · ${tool}`)
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
              activeDrawingTool={activeDrawingTool}
              drawings={drawings}
              selectedDrawingId={selectedDrawingId}
              onSelectDrawing={setSelectedDrawingId}
              onCreateDrawing={createDrawing}
              onUpdateDrawingPoint={updateDrawingPoint}
              onUpdatePositionWidth={updatePositionWidth}
              onDataApplied={recordChartData}
              renderChartOverlay={(chartApi, seriesApi) => (
                <FmsChartArrowOverlay
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
          {bottomDockWindow === 'activity' && <ActivityLogPanel entries={entries} onClear={clearActivity} />}
          {bottomDockWindow === 'calendar' && <EconomicCalendarPlaceholder />}
          {bottomDockWindow === 'past-result' && <FmsPastResultPanel result={selectedFmsResult} />}
        </BottomDockPanel>
      )}

      <footer className="status-bar">
        <span className="status-message"><i className="status-dot" /> Sample source · {sampleSymbolQuotes.length} symbols</span>
        <span className="status-selection">{selectedSymbol} · {timeframe} · {bars.length} bars</span>
        <div className="status-actions">
          <button className={`status-action${bottomDockWindow === 'activity' ? ' active' : ''}`} type="button" onClick={() => toggleBottomDock('activity')} aria-expanded={bottomDockWindow === 'activity'}>
            Activity <span className="activity-count">{entries.length}</span>
          </button>
          <button className={`status-action${bottomDockWindow === 'calendar' ? ' active' : ''}`} type="button" onClick={() => toggleBottomDock('calendar')} aria-expanded={bottomDockWindow === 'calendar'}>
            Calendar <span className="preview-label">Sample</span>
          </button>
          <ColorThemeButton onThemeChanged={changeTheme} />
          <button className={`status-action${settingsOpen ? ' active' : ''}`} type="button" onClick={() => setSettingsOpen((open) => !open)} aria-expanded={settingsOpen}>
            <span aria-hidden="true">⚙</span> Settings
          </button>
        </div>
      </footer>

      {settingsOpen && (
        <ChartSettingsPopover appearance={chartAppearance} onChange={changeChartAppearance} onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  )
}
