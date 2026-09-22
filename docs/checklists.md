# Deferred Improvement Checklists

Nice-to-have enhancements and future refinements identified during initial codebase review, deferred for consideration after core milestones.

---

## 1. Chart Drawings & Ergonomics

- [x] **Single Drawing Deletion (`Delete` / `Backspace` & UI action)**
  - Add single-item deletion function `deleteDrawing(id)` in `useChartDrawings`.
  - Listen for `Delete` / `Backspace` keydown events when a drawing is selected (`selectedDrawingId !== null`).
  - Provide an explicit delete / trash icon on or near the selected drawing handles or floating toolbar.
  - Record drawing deletion in UI Activity Log.

- [x] **Instrument-Aware Pip / Point Calculation in Position Tool**
  - Replace heuristic `entry.price > 20 ? 0.01 : 0.0001` in `PositionDrawing`.
  - Pass broker symbol precision (`digits` / `precision` from `SymbolQuote` or MT5 contract specs).
  - Calculate accurate pip/point value across commodities (e.g. XAUUSD), crypto (e.g. BTCUSD), and indices (e.g. US30/NAS100).

- [ ] **Drawing Style Customization (Optional)**
  - Allow user to adjust line thickness, color, or opacity for trendlines, rectangles, and channels.
  - Persist chosen defaults in `chart-drawing-storage`.

---

## 2. Chart Rendering & Candle Streaming

- [x] **Incremental Bar Updates (`series.update`)**
  - In `useMt5MarketData` / `MarketCandlestickChart`, utilize `series.update(lastBar)` for regular live candle polls (2-second interval).
  - Reserve full `series.setData(bars)` calls strictly for initial load, timeframe/symbol switching, or reconciliation.
  - Reduces chart redraw overhead and ensures smooth animation during high-frequency price ticks.

- [x] **Visible Logical Range Preservation During History Paging**
  - When older bars are prepended (demand-paging backwards), preserve logical bar indices (`getVisibleLogicalRange` / `setVisibleLogicalRange`) to avoid subtle time jumps near history boundaries.

---

## 3. Economic Calendar & Market Correlation

- [x] **Economic Event Markers on Chart Time Axis**
  - Correlate MT5 calendar events matching the active symbol's base/quote currencies (e.g. USD and EUR events for `EURUSD`).
  - Project vertical marker flags or pins on the chart at the exact `release_at` timestamp.
  - Clicking an event marker highlights the event in the Economic Calendar dock and displays release metrics (Actual vs Forecast).

- [ ] **Historical Impact Range Highlighting**
  - Option to visually shade the high-impact release candle / subsequent post-release volatility window on the chart.

---

## 4. Bridge & MT5 Observability

- [ ] **MT5 History Download Progress Indication**
  - When MT5 trade server has not yet downloaded historical bars locally, report sync status in the Activity Log or status bar so the user knows MT5 is actively downloading history from the broker.

- [x] **Active Terminal Process Selection Display**
  - If multiple MT5 terminals are installed, display the active terminal path or `FYODOR_MT5_TERMINAL_PATH` override status in the Data Heartbeat panel.

---

## 5. Phase 2: FMS Setup Engine Preparation

- [ ] **Stateless Pure-Function Design**
  - Keep core FMS calculation rules as pure functions `(bars, calendarEvents, parameters) => setups` isolated from UI and transport state.
  - Ensure setup rules are independently verifiable and testable without requiring an active MT5 connection.
