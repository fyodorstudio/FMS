# Fyodor Terminal — User & Operator Guide

Welcome to the **Fyodor Terminal**, an institutional-grade trading terminal built for quantitative macro-event arbitrage, real-time market analysis, and MetaTrader 5 connectivity.

---

## 1. Quick Start: One-Command Launch

Launch the entire ecosystem with a single command from the project root:

```bash
pnpm run dev:all
```

This starts all three decoupled services concurrently in your terminal:
1. 🟢 **BRIDGE** (`http://127.0.0.1:8001`): Native MetaTrader 5 IPC adapter.
2. 🟣 **FMS** (`http://127.0.0.1:8002`): Quantitative backtesting and signal engine.
3. 🔵 **UI** (`http://localhost:5173`): High-performance Vite terminal frontend.

Open your browser to **`http://localhost:5173`** to access the terminal.

---

## 2. Terminal Workspace Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ TOP BAR: Symbol Switcher | Timeframe (M1..D1) | Appearance | Clock Display   │
├────────────────────┬─────────────────────────────────────────────────────────┤
│ LEFT DOCK          │ CANDLESTICK CHART (Lightweight Charts)                  │
│ [Setups]           │ • Free 2D canvas pan & smooth zoom                      │
│ [Trade]            │ • Floating Drawing Toolbar                              │
│ [Journal]          │ • Top Notice Banner (history load & elapsed timer)      │
│                    │ • Timeline Calendar Strip (bottom pinned release badges)│
│                    │ • FMS Historical & Live Arrow Signal Projections        │
├────────────────────┴─────────────────────────────────────────────────────────┤
│ BOTTOM DOCK: [Economic Calendar] [Activity Log] [Data Heartbeat]             │
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
  - **Single-Click Placement**: Automatically sizes to **15 candles** of your active timeframe and a calibrated **timeframe-aware height** (no telephone-pole squishing).
  - **Four Corner Handles**:
    - *Top-left*: Adjusts Target (Take-Profit) price.
    - *Bottom-left*: Adjusts Stop-Loss price.
    - *Mid-left*: Dragging vertically alters the **Risk/Reward (TP/SL) ratio** directly by moving entry price without resizing the outer bounds.
    - *Mid-right*: Resizes box width through time.
  - **Move Entire Box**: Click and drag anywhere inside the green or red shaded area to move the entire position in price and time with zero width wiggling across weekends.
  - **Centered Labels**: Target, Entry, and Stop labels remain horizontally centered on the box at all times.
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

### D. Fyodor Macro Signal (FMS) Docks
Located in the Left Dock:

1. **Setups Dock (`[Setups]`)**:
   - The master playbook of codified, backtested setups.
   - Shows event name, target currency pair, recommended direction (BUY/SELL), empirical **Respect Rate** (e.g. $78\%$), sample size ($N=24$), and Risk/Reward ratio (e.g. $1:2.3$).
   - Click to expand for full statistical breakdown (MAE/MFE percentiles, S&R confluence rules).

2. **Trade Dock (`[Trade]`)**:
   - The live execution cockpit:
     - **Upcoming**: Countdown timer to imminent high-edge releases.
     - **Current (Active)**: Open macro swing positions tracking live excursion vs. target, P&L in pips, and current $R$.
     - **Recent**: Closed trades awaiting review with outcome badges.

3. **Journal Dock (`[Journal]`)**:
   - The performance ledger tracking cumulative $R$-multiple growth (+12.4R), win rate %, profit factor, and average $R$ per trade.
   - Interactive cumulative $R$-curve visualization over time.

---

## 4. How to Run Backtests & Research with AI

You do not need to write code to research new setups. You can instruct the AI assistant directly:

```
"Gemini, backtest US Core CPI on USDJPY H4 across the last 3 years.
If it shows over 65% respect rate with at least 1:1.5 R:R, register the setup."
```

The assistant will:
1. Trigger the isolated FMS engine in `fms/`.
2. Extract historical H4 candles and calendar prints from the local bridge.
3. Compute $Z$-score surprise deviations and vectorized MAE/MFE excursions.
4. Derive statistical Stop-Loss ($85\text{th}$ percentile MAE) and Take-Profit (median MFE).
5. Register the setup into the local SQLite store (`fms/data/fms_store.db`), making it immediately visible in your Left Dock and Chart Arrows.

---

## 5. Troubleshooting & FAQ

- **MT5 Terminal Disconnected**: Check the bottom dock **Data Heartbeat** tab. It shows your broker login, server generation, and native adapter PID. Restart MT5 and the bridge will automatically reconnect within 2 seconds.
- **Chart Lag or Freezes**: Fyodor preserves canvas contexts across symbol switches. If your broker takes 20+ seconds to download deep history on an uncached CFD, the top notice banner will show active progress while the rest of the terminal remains 100% interactive.
- **Port Conflicts**:
  - Bridge uses port `8001`
  - FMS Engine uses port `8002`
  - Frontend uses port `5173`
