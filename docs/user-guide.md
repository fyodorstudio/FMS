# Fyodor Terminal — User & Operator Guide (Canvas & Notebook)

Welcome to the **Fyodor Terminal**, a high-performance trading terminal and forensic notebook built for discretionary market analysis, disciplined trade execution planning, and live MetaTrader 5 connectivity.

---

## 1. Quick Start: One-Command Launch

Launch the entire ecosystem with a single command from the project root:

```powershell
pnpm run dev:all
```

This starts the decoupled services concurrently:
1. 🟢 **BRIDGE** (`http://127.0.0.1:8001`): Native MetaTrader 5 IPC adapter.
2. 🔵 **UI** (`http://localhost:5173`): High-performance Vite terminal frontend.

Open your browser to **`http://localhost:5173`** to access the terminal.

---

## 2. Terminal Workspace Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: Symbol Switcher | Timeframe (M1..MN) | Appearance | Clock Display   │
├────────────────────┬─────────────────────────────────────────────────────────┤
│ LEFT DOCK          │ CANDLESTICK CHART (Lightweight Charts)                  │
│ [Market Watch]     │ • Free 2D canvas pan & smooth zoom                      │
│                    │ • Floating Drawing Toolbar                              │
│                    │ • Top Notice Banner (history load & elapsed timer)      │
│                    │ • Timeline Calendar Strip (bottom pinned release badges)│
│                    │ • Planned Trade Horizontal Lines (Entry, TP, SL)        │
├────────────────────┴─────────────────────────────────────────────────────────┤
│ BOTTOM DOCK: [Notebook] [Economic Calendar] [Activity Log]                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ STATUS BAR: MT5 Terminal State | Clock Offset | Generation Counter | Latency │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Features & Controls

### A. Candlestick Chart Navigation
- **Free 2D Pan**: Click and drag anywhere on the chart canvas to move both horizontally through time and vertically across price levels with 1:1 cursor tracking.
- **Auto-Scale Snap**: Double-click the chart canvas or the vertical price axis to instantly re-center and auto-scale.
- **Timeframe Selector**: Toggle between `M1`, `M5`, `M15`, `M30`, `H1`, `H4`, and `D1`.
- **Remote History Paging**: When scrolling back into historical bars or switching to a new symbol, a top notice banner appears:
  `Loading older candles · 3.4s · Requesting broker candle history for EURUSD H4…`
  The live elapsed counter keeps you informed while MT5 downloads remote broker history.

---

### B. Drawing Tools & Long/Short Position Tool
The floating toolbar on the left of the chart hosts institutional drawing tools:
- **Long / Short Position Tool**:
  - **Single-Click Placement**: Automatically sizes to **15 candles** of your active timeframe and a calibrated **timeframe-aware height**.
  - **Four Corner Handles**:
    - *Top-left*: Adjusts Target (Take-Profit) price.
    - *Bottom-left*: Adjusts Stop-Loss price.
    - *Mid-left*: Dragging vertically alters the **Risk/Reward (TP/SL) ratio** directly by moving entry price without resizing the outer bounds.
    - *Mid-right*: Resizes box width through time.
  - **Move Entire Box**: Click and drag anywhere inside the green or red shaded area to move the entire position in price and time.
- **Right-Click Direct Deletion**: Right-click directly on any line, shape, or position box to immediately remove it.
- **Text Drawing Tool**: Click to place, type directly inline without tick interruptions, press Enter to commit, and double-click to re-edit.

---

### C. Economic Calendar & Timeline Strip
- **Timeline Strip**: Economic releases are pinned to a clean timeline strip $28\text{px}$ above the time axis.
  - 🔴 **Red dot**: High impact release.
  - 🟡 **Yellow dot**: Medium impact release.
  - Currency badge (e.g. `USD (3)`): Grouped releases occurring on that candle.
- **Hover Inspection Card**: Hover over any timeline badge to see event title, release time, actual vs. forecast vs. previous values.
- **Click-to-Highlight Table Jump**: Clicking any badge opens the bottom dock to the **Economic Calendar**, scrolls the virtualized table directly to that release, and pulses the row with a bright blue glow.

---

### D. Trader's Notebook & Execution Planner
Located in the Bottom Dock under the **Notebook** tab:
1. **Planned Execution Levels**:
   - Direction toggle: `LONG (BUY)` or `SHORT (SELL)`.
   - Entry, Take Profit, and Stop Loss price inputs with "Use Market" shortcut.
   - Computes target distance in pips, stop distance in pips, and exact **Reward-to-Risk ratio** (e.g. `1 : 1.50R`).
2. **Project on Chart**:
   - Check the box to project the clean horizontal lines directly on the candlestick chart:
     - **Entry**: Dotted blue line (`#0284c7`).
     - **Take Profit**: Dashed emerald line (`#10b981`).
     - **Stop Loss**: Dashed rose line (`#e11d48`).
3. **Durable Forensic Journal**:
   - Rich `<textarea>` for thesis, catalyst notes, or trade audits, automatically saved in `localStorage` keyed to each symbol (`trader_notebook_note_${symbol}`). When you switch symbols, your notes for that symbol load instantly.

---

## 4. Troubleshooting & FAQ

- **MT5 Terminal Disconnected**: Check the bottom dock **Activity Log** / Data Heartbeat. It shows your broker login, server generation, and native adapter PID. Restart MT5 and the bridge will automatically reconnect within 2 seconds.
- **Port Assignment**:
  - Bridge uses port `8001`
  - Frontend uses port `5173`
