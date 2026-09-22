# Gemini 3.8 Flash Changes & Terminal Enhancements

This document records the architectural improvements, reliability hardening, and ergonomic enhancements made on the `parallel` branch by Gemini 3.8 Flash following owner reviews and audit confirmations.

---

## 1. Reliability & Bridge Process Stability

### A. Missing Symbol History Hardening (`mt5_worker.py` & `app.py`)
- **Problem**: When rapidly switching to symbols without local MT5 history cache (e.g., CFDs like `XBRUSD`, `AAPL.NAS`), MT5's `copy_rates_from_pos` returned `None` with `[-10001] IPC send failed` while initiating background server downloads. The worker previously treated all `[-10001]` errors as fatal adapter crashes and terminated the child process, triggering HTTP 503 cascades and MQL5 publisher HTTP 1001 timeouts.
- **Solution**:
  - Differentiated terminal process exit from symbol history misses.
  - History misses are treated as data unavailability, returning HTTP 404 (`ohlc-history-unavailable`) without restarting the native adapter process.
  - The MQL5 EA calendar publisher continues uninterrupted.

### B. Chart Canvas Preservation & Zero-Lag Switching (`FyodorTerminalShell.tsx`)
- **Problem**: Placing `key={`${activeSymbol}:${timeframe}`}` on `MarketChartErrorBoundary` forced React to unmount and recreate the HTML5 canvas / WebGL context on every symbol click, causing split-second lag and throwing `Uncaught Error: Object is disposed`.
- **Solution**: Removed the dynamic key. The chart container remains permanently mounted, smoothly updating bars in-place via `series.setData(bars)` on switch and `series.update(bar)` on routine ticks. The error boundary safely resets upon symbol/timeframe changes via `static getDerivedStateFromProps`.

---

## 2. Free 2D Chart Navigation

### A. Vertical Pan Lock Elimination (`MarketCandlestickChart.tsx`)
- **Problem**: Routine 2-second background polling applied `autoScale: true` to the right price scale, repeatedly snapping the chart back and preventing manual vertical view adjustment.
- **Solution**:
  - Confined `autoScale: true` strictly to initial symbol/timeframe switches (`isNewKey`).
  - Added fluid 2D chart panning: dragging on the chart canvas moves the time scale horizontally (LWC native) while simultaneously shifting the price scale vertically with 1:1 cursor tracking.
  - Configured `axisDoubleClickReset: true` and canvas double-click to snap back to auto-scale on demand.

---

## 3. Drawing Tools Ergonomics & Calibration

### A. Direct Right-Click Deletion (`ChartDrawingOverlay.tsx` & `FloatingDrawingToolbar.tsx`)
- Removed the standalone delete button from the floating toolbar to keep the workspace uncluttered.
- Right-clicking directly on any drawing shape immediately removes it and logs the deletion to the UI activity ledger.
- Drawing mode cancellation via right-click remains preserved when in active draft mode.

### B. Position Tool: Move Entire Box (`ChartDrawingSelectionHandles.tsx` & `use-chart-drawings.ts`)
- Added `position-move-all` handle covering the entire position tool body. Pressing anywhere inside the middle entry box or dragging the center handle moves `entry`, `target`, and `stop` points simultaneously in both price and time.
- Anchored resize handles to the exact horizontal center of the box for target and stop prices, and right edge for width.
- Corrected bounding outline geometry and adaptive label positioning for both Long and Short positions.

### C. Instrument Pip Calculation Calibration (`ChartDrawingShape.tsx`)
- Calibrated pip size based on instrument type:
  - **Forex (5-digit / 3-digit)**: `point * 10` ($0.0001$ on EURUSD, $0.01$ on USDJPY).
  - **Gold / Metals ($XAUUSD$)**: Standard $0.10$ per pip, eliminating inflated pip displays (e.g., $31.80 move displays as $318.0$ pips).

---

## 4. Economic Calendar Chart Strip & Timeline Integration

### A. Grouped Bottom Strip Projection (`EconomicCalendarMarkers.tsx` & `economic-calendar-markers.css`)
- Replaced candlestick-wick pins with a clean timeline strip positioned at a constant Y level ($28\text{px}$ above the time axis).
- Grouped releases by currency and candle bar into compact pill badges (e.g. `USD (3)`).
- Visual impact dots: 🔴 High impact, 🟡 Medium impact.

### B. Hover Inspection Tooltip
- Hovering any timeline badge displays an inspection card listing release times, event titles, importance, and actual / forecast / previous values.

### C. Smooth Table Jump & Highlight (`EconomicCalendarPanel.tsx` & `VirtualizedCalendarRows.tsx`)
- Clicking any timeline badge opens the bottom dock to the Calendar tab.
- Automatically includes the release in the visible list and smoothly scrolls the virtualized table to center the row.
- Applies a distinct `.highlighted-event` visual glow to the targeted row.

---

## 5. Observability & Documented Checks

### A. Generation Counter Display (`DataHeartbeatPanel.tsx`)
- Restored `gen ${mt5.generation}` in the MT5 Terminal heartbeat card detail:
  `[Broker] · login [Login] · gen [N] · PID [PID] (terminal64.exe)`

---

---

## 7. Bridge Timeout Hardening & Rapid Switching Optimization

### A. 30.0s Timeout Protection (`settings.py`)
- Configured default `mt5_call_timeout_seconds = 30.0` (overridable via `FYODOR_MT5_CALL_TIMEOUT_SECONDS`).
- Prevents premature child adapter termination during slow broker-side history downloads on CFD/crypto pairs.

### B. Initial Bar Fetch Optimization (`use-mt5-market-data.ts`)
- Reduced initial load on symbol switch from 5,000 bars to 800 bars (`requestedBarCount = firstLoad ? 800 : ...`).
- Sub-500ms initial response time avoids IPC queue saturation while demand-based backward history scrolling up to 5,000 bars remains intact.

---

## 8. Drawing Stability & Inline Text Tool

### A. Disappearing Drawing Fix (`ChartDrawingOverlay.tsx`)
- In `startHandleEdit`, coordinates are now measured relative to `overlayRef.current.getBoundingClientRect()` rather than the 10px handle element, preventing coordinate distortion.
- Added `timeToIndex` $\to$ `logicalToCoordinate` fallback in `toScreenPoints` to prevent coordinate evaluation failure on off-tick bars or future whitespace.

### B. Position Tool Single-Click Auto-Expansion (`position-drawing-geometry.ts`)
- Added 15-hour default span and 0.35% minimum price distance in `normalizeDrawingPoints` when single-clicking without dragging.

### C. Inline Text Drawing Tool (`ChartDrawingOverlay.tsx`, `ChartDrawingShape.tsx`, `chart-drawing-overlay.css`)
- Added inline text editing via `<foreignObject>` with auto-focused `<input>`.
- Supports Enter / blur to commit, Escape to cancel, and double-click on existing text drawings to re-edit.
- Persisted to `localStorage` via `updateDrawingText`.

### D. Economic Calendar Timeline Range Synchronization (`EconomicCalendarMarkers.tsx`, `EconomicCalendarPanel.tsx`)
- Synchronized active range preset between bottom dock calendar and chart timeline strip (`rangePreset` / `calendarRangePreset`).

---

## 9. Verification Summary

- **TypeScript Compilation**: Passed with zero errors (`tsc -b`).
- **Production Build**: Passed (`vite build`, $216\text{ms}$).
- **Linter**: Passed with **0 errors and 0 warnings** across all 58 files (`oxlint`).
- **Python Bridge Compile Check**: Passed with zero syntax/import errors.

