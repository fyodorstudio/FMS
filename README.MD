# NO-AI 
A fresh new start. The messy terminal is no longer trusted because how differing AI models and versions across 8+ Months has been tangling and further causing the repo to be this unnecessarry complex blob of a mess.

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
Activity heartbeat. It binds only to `127.0.0.1:8001`, reads visible Market
Watch symbols and selected-chart OHLC, and accepts economic-calendar data from
the read-only MQL5 publisher. It has no order endpoint and no persistent market
data cache. See `bridge/README.md` for the one-time calendar publisher setup and
the acceptance checklist.

## Rebuilding plan

1. Data Collection

- build UI to show all the available data that mt5 can provide such as 
  - economic calendar table 
  - lightweight charts to show OHLC

- build the python bridge and clear logging to ensure data arrived correctly, will explicitly reuse the mql5 script already compiled and attached in mt5

2. Data Calculation

- build fms panel which consists of
  - Trade dock to see upcoming, current, recent registered setup
  - fms workbench to craft the registered setup
