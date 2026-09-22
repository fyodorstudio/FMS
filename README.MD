# NO-AI 
A fresh new start. The messy terminal is no longer trusted because how differing AI models and versions across 8+ Months has been tangling and further causing the repo to be this unnecessarry complex blob of a mess.




















## Repository Documentation Directory (Frozen Index)

All repository documentation is consolidated and strictly mapped as follows:

| Document | Location | Purpose & Audience |
| :--- | :--- | :--- |
| **Root Overview** | [`README.MD`](file:///c:/dev/NO-AI/README.MD) | System overview, topology, and quickstart commands. |
| **User & Operator Guide** | [`docs/user-guide.md`](file:///c:/dev/NO-AI/docs/user-guide.md) | Terminal operator manual (chart controls, drawing tools, docks, launch). |
| **Engineering Rules** | [`docs/AGENTS/AGENTS.md`](file:///c:/dev/NO-AI/docs/AGENTS/AGENTS.md) | Strict coding rules, domain boundaries, no barrel files, zero generic folders. |
| **Research Paper** | [`docs/RESEARCH PAPER/README.md`](file:///c:/dev/NO-AI/docs/RESEARCH%20PAPER/README.md) | Modular quantitative research paper (Foundations, Excursions, Physics, Depth, Synthesis). |
| **Terminal Changelog** | [`docs/DEVELOPMENT LOGS/gemini-changes.md`](file:///c:/dev/NO-AI/docs/DEVELOPMENT%20LOGS/gemini-changes.md) | Architectural fixes, reliability hardening, chart & drawing ergonomics. |
| **Audit Checklist** | [`docs/DEVELOPMENT LOGS/checklists.md`](file:///c:/dev/NO-AI/docs/DEVELOPMENT%20LOGS/checklists.md) | Feature audit and manual verification checklist. |
| **FMS Engine Master Guide**| [`fms/README.MD`](file:///c:/dev/NO-AI/fms/README.MD) | Single-source master documentation for FMS (5-Factor Framework, API, CLI, Tests). |
| **FMS Library (Web UI)**   | [`http://127.0.0.1:8002/`](http://127.0.0.1:8002/) | Interactive Uxcel-style catalog, Monolith quant gauges, and setups portal. |
| **MT5 Bridge Guide** | [`bridge/README.md`](file:///c:/dev/NO-AI/bridge/README.md) | MT5 read-only bridge adapter setup, MQL5 publisher, and IPC architecture. |

---

## Explicit rules
- No AI code write
- Trusted Data still comes from user-logged in broker > MT5 > this app, strictly :
  1. OHLC Candle
  2. economic calendar

## Main Goal of this App
- app collects OHLC and Economic calendar from MT5
- app FMS calculate those two data to produce registered setups to gain edge in trading and to help trader to see when an event in economic calendar releases how price reacts.

## Stack
- Python for bridge and MT5 integration
- Typescript for UI

## Rebuilding plan

1. Data Collection

- build UI to show all the available data that mt5 can provide such as 
  - economic calendar table 
  - lightweight charts to show OHLC

- build the python bridge and clear logging to ensure data arrived correctly, will explicitly use the mql5 script 
 compiled and attached in mt5

2. Data Calculation

- build fms panel which consists of
  - Trade dock to see upcoming, current, recent registered setup (lives in /frontend)
  - fms workbench to craft the registered setup (lives in /FMS)

## Development startup
First-time bridge setup:

```powershell
python -m venv bridge/.venv
bridge/.venv/Scripts/python.exe -m pip install -e ./bridge
pnpm install
```

Normal startup:

```powershell
pnpm run dev:all
```
The bridge stays alive when MT5 is closed and reports that state to the in-app
Activity heartbeat. Native MetaTrader5 calls are isolated in a supervised child
process so failed broker IPC cannot block bridge health. It binds only to
`127.0.0.1:8001`, reads visible Market Watch symbols, demand-pages the selected
chart's available OHLC history, and accepts economic-calendar data from the
read-only MQL5 publisher. It has no order endpoint and no persistent market data
cache. See `bridge/README.md` for the one-time calendar publisher setup and the
acceptance checklist.

### FMS Library (Web UI & Strategy Portal) Launch
The **FMS Library** is served independently by the isolated FMS engine:

```powershell
.\fms\.venv\Scripts\python.exe fms/run_dev.py
```
Then navigate in your web browser:
- **FMS Library Web UI**: [http://127.0.0.1:8002/](http://127.0.0.1:8002/) (or `/portal`)
- **Interactive API Swagger**: [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)





┌────────────────────────────────────────────────────────────────────────┐
│                         FYODOR TERMINAL (FRONTEND)                     │
│   • Renders 60 FPS charts, Setups, Trade, and Journal Docks            │
│   • Receives pre-computed, lightweight JSON payloads only              │
└───────────────────────▲────────────────────────▲───────────────────────┘
                        │                        │
       Raw Market Data  │                        │ Clean FMS Payloads
       (Quotes/Candles) │                        │ (Setups/Trades/Arrows)
                        │                        │
┌───────────────────────┴──────────────┐ ┌───────┴───────────────────────┐
│              MT5 BRIDGE              │ │          FMS ENGINE           │
│         (port 8000 / FastAPI)        │ │         (Isolated App)        │
│   • Native MetaTrader5 IPC adapter   │ │   • Vectorized Polars/NumPy   │
│   • Pure read-only candle/calendar   │ │   • MAE / MFE Distributions   │
│   • Zero strategy logic              │ │   • S&R Liquidity Zones       │
└───────────────────────┬──────────────┘ │   • SQLite Setup Registry     │
                        │                │   • Research CLI Workbench    │
                        └─ Ingestion ───►└───────────────────────────────┘