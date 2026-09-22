# Fyodor Macro Signal (FMS) — Quantitative Engine & Framework

## 1. Executive Summary & Philosophy

**Fyodor Macro Signal (FMS)** is a systematic quantitative macro-swing framework built as an isolated research and signal engine under `fms/`.

### Core Philosophy
> *"Market microstructure and macroeconomic narratives are filled with noise. We do not need to understand every fundamental variable driving price; we only need to know whether price historically exhibited a repeatable, statistically profitable reaction following a specific economic release."*

### Key Operating Principles
1. **Swing Horizon Over Noise**: Instead of scalping the chaotic first 5 minutes of a news release, FMS operates on **H1 and H4** timeframes. Post-Announcement Currency Drift (PACD) reaches empirical crest as institutional portfolios rebalance allocations.
2. **Empirical Edge (Respect vs. Disrespect)**: Economic theory dictates what a release *should* mean. FMS measures what price *actually does* across multi-year history, computing path-dependent **Respect Rates** and cumulative $R$-multiples directly from broker candles.
3. **Data-Driven Dynamic Risk (ATR Invariance)**: Stop-loss and take-profit levels are never arbitrary guesses; they are derived from historical **Maximum Adverse Excursion (MAE)** and **Maximum Favorable Excursion (MFE)** normalized by **Average True Range ($\text{ATR}_{14}$)**. Stops and targets breathe dynamically with market volatility.
4. **2D Liquidity Confluence (S&R Filter)**: Macro momentum triggers are filtered against structural support and resistance with a forgiving $2.0 \times \text{ATR}$ buffer—avoiding buying into overhead resistance or selling into structural support.
5. **Multi-Model Quantitative Framework**: Different economic events represent different market mechanisms. FMS organizes setups into **5 distinct quantitative factor methods**, each clearly labeled on registered setups.

---

## 2. FMS Library (Web UI — Uxcel Catalog & Monolith Gauges)

FMS includes a dedicated, self-contained interactive web library served directly by the engine:

### How to Launch & Access:
1. Start the FMS engine from the project root:
   ```powershell
   .\fms\.venv\Scripts\python.exe fms/run_dev.py
   ```
2. Open your web browser and navigate to:
   - **FMS Library**: [http://127.0.0.1:8002/](http://127.0.0.1:8002/) (or [http://127.0.0.1:8002/portal](http://127.0.0.1:8002/portal))
   - **Interactive API Swagger**: [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)

### FMS Library Features:
- **Uxcel-Style Topic Catalog**: Alphabet filter bar (`ALL`, `A`, `C`, `E`, `M`, `P`, `S`, `Z`) and real-time search input across quant and microstructure concepts.
- **Dedicated Topic Detail Pages**: Clicking any topic card opens a full detail page with breadcrumbs (`← Back to FMS Library`), plain-language articles, interactive Accordion FAQs, core quantitative rules, and cross-links to registered setups.
- **Monolith Quant View**: Dynamic SVG Arc Gauges for Composite Respect Rate and Expected Value ($E[R]$), the R:R Decay Curve visualization, and event-family peak duration charts dynamically computed from active setups.
- **Codified Setups Grid**: Interactive cards displaying active statistical setups, typical pips, ATR formulas, win rates, and fundamental theses loaded directly from `fms_store.db`.
- **Empirical Macroeconomic Audit Table**: Dynamic path-evaluated matrix computed across verified broker H1 candles and 126,469 macroeconomic events.

---

## 3. CLI Research Workbench & Calibration

FMS provides a command-line interface for research, calibration, and setup inspection:

```powershell
# 1. View all active codified setups saved in SQLite
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main setups

# 2. Run empirical setup calibrator across broker candle history
.\fms\.venv\Scripts\python.exe -m fms_engine.strategy.setup_calibrator

# 3. View API health and summary
curl http://127.0.0.1:8002/api/fms/health
curl http://127.0.0.1:8002/api/fms/summary
```

---

## 4. Empirical Quality Gate Criteria

Every registered setup in the FMS SQLite store must satisfy strict mathematical criteria derived from historical broker data:
- **Sample Count ($N$)**: $N \ge 15$ verified event occurrences to capture quarterly and central bank releases (e.g. FOMC, ECB, GDP) without discarding low-frequency high-conviction catalysts.
- **Respect Rate (Win Rate)**: $\text{Respect Rate} \ge 50.0\%$.
- **Mathematical Expectancy**: $\text{Net } R > 0.0R$ across the historical observation period.
- **Reward-to-Risk Ratio ($R:R$)**: $R:R \ge 1.00$.

All metrics are 100% reproducible from raw broker candle files on disk (`fyodor_candles/`) and the master calendar history (`fyodor_calendar_master_history.csv`).

---

## 5. Multi-Method Quantitative Factor Taxonomy

FMS models macro trading across currencies and commodities through 5 distinct quantitative methods:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FMS MULTI-METHOD TAXONOMY                       │
├────────────────────────────────────────────────────────────────────────┤
│ Method 1: [M-MSD] Macro Surprise Divergence (PACD)                     │
│ • Rolling standardized surprise vector spread between two currencies   │
│ • S&R Zone Confluence + ATR Dynamic Volatility Scaling.                │
├────────────────────────────────────────────────────────────────────────┤
│ Method 2: [M-PYS] Policy & Real Yield Spread Momentum                  │
│ • Central bank rate divergence & Irving Fisher Real Yield Spreads.     │
│ • S&R Zone Confluence + Multi-Week Drift Acceleration.                 │
├────────────────────────────────────────────────────────────────────────┤
│ Method 3: [M-TOT] Terms-of-Trade Commodity Pulse                       │
│ • Commodity export shocks on commodity currencies (AUD, CAD, NZD).     │
│ • Relative divergence against net energy/metal importers (JPY, EUR).   │
├────────────────────────────────────────────────────────────────────────┤
│ Method 4: [M-VRC] Volatility Regime & Carry Unwind                     │
│ • Regime-switching model tracking FX volatility spikes vs. carry yield.│
│ • Exploits quiet carry drift vs. violent safe-haven rushes (JPY, CHF). │
├────────────────────────────────────────────────────────────────────────┤
│ Method 5: [M-LAR] Liquidity Absorption Rejection                       │
│ • The Mirror Principle: 1.5x+ ATR expansion and 40%+ rejection wicks.  │
│ • Sovereign defense absorption footprint off structural S&R zones.     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Directory Layout & Architecture

```
fms/
├── pyproject.toml              # Dependencies (polars, numpy, fastapi, uvicorn, typer, rich)
├── run_dev.py                  # Standalone local dev runner (port 8002)
├── README.MD                   # Master FMS documentation (this file)
├── data/                       # Local compressed caches & SQLite store (gitignored)
│   ├── cache/                  # Parquet candle & calendar historical caches
│   └── fms_store.db            # SQLite: registered setups, active trades, journal ledger
├── tests/                      # Unit test suite (pytest)
│   └── test_fms_analytics.py   # Automated unit tests
└── src/
    └── fms_engine/
        ├── config.py           # Paths, ports, ATR/MAE/MFE parameters
        ├── api/                # FastAPI endpoints & dynamic HTML portal
        ├── analytics/          # Factor models, S&R detector, signal evaluator
        ├── contracts/          # Pydantic models for events, setups, trades, journal
        ├── ingestion/          # Parquet loaders for MT5 candles & calendar
        └── strategy/           # Setup registry, calibrator, trade tracker, journal
```

---

## 7. Data Integrity Covenant

FMS adheres strictly to the repository-wide **Anti-Hallucination Covenant**:
- **Zero Synthetic / Mock Data**: All candle observations and calendar events originate from real broker exports.
- **Zero Modulo Outcome Faking**: Every signal, trade outcome, and excursion metric is path-evaluated bar-by-bar against actual historical high/low candle boundaries.
- **Zero Forward Lookahead**: All evaluators strictly enforce causal access (`candles[:i]`).
