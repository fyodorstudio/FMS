# Part 3: Isolated System Architecture & Topology

## 1. Decoupled Three-Tier Topology

To ensure zero latency impact on frontend chart rendering and isolate execution failures, FMS is architected across three independent tiers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          1. FRONTEND TERMINAL                           │
│  • Lightweight Charts Canvas & Vectorized Drawing Overlay               │
│  • Registered Setups Dock (Playbook / Inspection)                       │
│  • Trade Dock (Upcoming Countdown, Active Excursion, Closed History)   │
│  • Journal Dock (Cumulative R-Curve, Post-Registration Auditing)        │
│  • Zero calculation overhead; renders pre-computed DTOs only            │
└───────────────────▲─────────────────────────────────▲───────────────────┘
                    │                                 │
                    │ /api/v1/market-watch            │ /api/fms/setups
                    │ /api/v1/ohlc                    │ /api/fms/trades
                    │                                 │ /api/fms/signals
┌───────────────────┴─────────────────┐   ┌───────────┴───────────────────┐
│           2. MT5 BRIDGE             │   │         3. FMS ENGINE         │
│  • Python MetaTrader5 Client        │   │  • Macro Event Normalizer     │
│  • Serialized Latest-Wins Queue     │   │  • Vectorized Backtest Worker │
│  • Pure Read-Only Data Adapter      │   │  • MAE/MFE Percentile Engine  │
│  • Zero Strategy Logic              │   │  • Liquidity Zone Detector    │
└───────────────────┬─────────────────┘   └───────────▲───────────────────┘
                    │                                 │
                    └────── Local Data Pipeline ──────┘
                      (FMS ingests candles & calendar
                       from local bridge adapter)
```

## 2. Tier Responsibilities

1. **Frontend Presentation (`frontend/src/`)**: 
   - React + TypeScript terminal running at 60 FPS.
   - Strictly consumes pre-calculated DTOs via `/api/fms/*`.
2. **Bridge Adapter (`bridge/src/`)**: 
   - Isolated Python environment (`bridge/.venv`) interfacing with MetaTrader 5 IPC pipes on port **8001**.
   - Read-only data adapter for live OHLC tick data and economic calendar streams.
3. **FMS Quantitative Engine (`fms/src/`)**: 
   - Isolated Python environment (`fms/.venv`) running API server on port **8002**.
   - High-performance analytical compute using **Polars** and **NumPy**.
   - Local Parquet caching (`fms/data/cache/`) and SQLite storage (`fms/data/fms_store.db`).
