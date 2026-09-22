# Fyodor Macro Signal (FMS) — Quantitative Engine & Framework

## 1. Executive Summary & Philosophy

**Fyodor Macro Signal (FMS)** is a systematic quantitative macro-swing framework built as an isolated research and signal engine under `fms/`.

### Core Philosophy
> *"Market microstructure and macroeconomic narratives are filled with noise. We do not need to understand every fundamental variable driving price; we only need to know whether price historically exhibited a repeatable, statistically profitable reaction following a specific economic release."*

### Key Operating Principles
1. **Swing Horizon Over Noise**: Instead of scalping the chaotic first 5 minutes of a news release, FMS operates on **H4 and D1** timeframes. Post-Announcement Currency Drift (PACD) reaches empirical crest at **24 to 28 H4 bars ($\approx 4.0\text{--}4.7$ trading days)** as institutional portfolios rebalance allocations.
2. **Empirical Edge (Respect vs. Disrespect)**: Economic theory dictates what a release *should* mean. FMS measures what price *actually does* across 10 years of history, computing path-dependent **Respect Rates** and cumulative $R$-multiples.
3. **Data-Driven Dynamic Risk (ATR Invariance)**: Stop-loss and take-profit levels are never arbitrary guesses; they are derived from historical **Maximum Adverse Excursion (MAE)** and **Maximum Favorable Excursion (MFE)** normalized by **Average True Range ($\text{ATR}_{14}$)**. Stops and targets breathe dynamically with market volatility.
4. **2D Liquidity Confluence (S&R Filter)**: Macro momentum triggers are filtered against high-timeframe order blocks with a forgiving $2.0 \times \text{ATR}$ buffer—never buying into overhead resistance or selling into structural support.
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
- **Uxcel-Style Topic Catalog**: Alphabet filter bar (`ALL`, `A`, `C`, `E`, `M`, `P`, `S`, `Z`) and real-time search input across all quant and microstructure concepts.
- **Dedicated Topic Detail Pages**: Clicking any topic card opens a full Uxcel-style detail page with breadcrumbs (`← Back to FMS Library`), plain-language articles, interactive Accordion FAQs, core quantitative rules, and cross-links to registered setups.
- **Monolith Quant View**: High-precision SVG Arc Gauges for Composite Respect Rate (58.8%) and Expected Value (+0.26R/trade), the R:R Decay Curve visualization, and event-family peak duration bar charts.
- **Codified Setups Grid**: Interactive cards displaying all 8 passing statistical setups, typical pips, ATR formulas, win rates, and plain-English fundamental theses.
- **10-Year Decadal Audit Table**: Full 24-combination matrix across 166,283 H4 candles (2017–2026), detailing the microstructure behind directional asymmetry (Why Short USD setups crush Long USD setups).

---

## 3. CLI Research Workbench

FMS provides a fast command-line interface for research, calibration, and setup inspection:

```powershell
# 1. View all active codified setups saved in SQLite
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main setups

# 2. Run full 10-year decadal research cruncher for Method 1 ([M-MSD])
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main research --method msd --min-spread 1.75 --horizon 24 --zones

# 3. Run full 10-year decadal research cruncher for Method 2 ([M-PYS])
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main research --method pys --horizon 24 --zones

# 4. Auto-register passing setups into SQLite store
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main research --method msd --register
.\fms\.venv\Scripts\python.exe -m fms_engine.cli.main research --method pys --register
```

---

## 4. Empirical 10-Year Decadal Audit Results (2017–2026)

Tested across 166,283 H4 bars and 1,847 macroeconomic events under the Quality Gate ($\text{Win Rate} \ge 50\%$, $\text{Net } R > 0.0R$, $R:R \ge 1.00$, $N \ge 8$):

### Method 1: [M-MSD] Macro Surprise Divergence (Tactical Shocks)
| Symbol | Direction | Sample ($N$) | W / L | Win Rate | Median TP / SL | SL ATR | $R:R$ | Net Realized $R$ | EV / Trade | Avg Duration | Edge Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EURUSD** | **BUY** | 16 | 9 / 7 | **56%** | $63\text{p} / 42\text{p}$ | $1.5\times$ | **1.50** | **+6.5R** | **+0.41R** | $7.8\text{ bars}$ | **PASS** |
| **GBPUSD** | **BUY** | 22 | 14 / 8 | **64%** | $88\text{p} / 70\text{p}$ | $2.0\times$ | **1.25** | **+7.5R** | **+0.34R** | $11.5\text{ bars}$ | **PASS** |
| **USDJPY** | **SELL** | 15 | 9 / 6 | **60%** | $41\text{p} / 41\text{p}$ | $1.5\times$ | **1.00** | **+4.3R** | **+0.29R** | $8.3\text{ bars}$ | **PASS** |
| **AUDUSD** | **BUY** | 19 | 11 / 8 | **58%** | $86\text{p} / 57\text{p}$ | $2.5\times$ | **1.50** | **+6.6R** | **+0.35R** | $16.8\text{ bars}$ | **PASS** |
| **AUDUSD** | **SELL** | 19 | 10 / 9 | **53%** | $55\text{p} / 55\text{p}$ | $2.5\times$ | **1.00** | **+0.4R** | **+0.02R** | $14.4\text{ bars}$ | **PASS** |
| **USDCAD** | **SELL** | 18 | 9 / 9 | **50%** | $99\text{p} / 66\text{p}$ | $2.5\times$ | **1.50** | **+2.1R** | **+0.12R** | $14.9\text{ bars}$ | **PASS** |
| **USDCHF** | **SELL** | 12 | 7 / 5 | **58%** | $43\text{p} / 43\text{p}$ | $2.0\times$ | **1.00** | **+2.0R** | **+0.17R** | $10.8\text{ bars}$ | **PASS** |
| **NZDUSD** | **BUY** | 10 | 7 / 3 | **70%** | $31\text{p} / 31\text{p}$ | $1.5\times$ | **1.00** | **+4.0R** | **+0.40R** | $7.4\text{ bars}$ | **PASS** |

### Method 2: [M-PYS] Policy & Real Yield Spread Momentum (Sovereign Gravity)
| Symbol | Direction | Sample ($N$) | W / L | Win Rate | Median TP / SL | SL ATR | $R:R$ | Net Realized $R$ | EV / Trade | Avg Duration | Edge Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AUDJPY** | **BUY** | 130 | 76 / 54 | **58%** | $96\text{p} / 77\text{p}$ | $2.0\times$ | **1.25** | **+29.7R** | **+0.23R** | $12.0\text{ bars}$ | **PASS** |
| **AUDUSD** | **SELL** | 70 | 35 / 35 | **50%** | $60\text{p} / 48\text{p}$ | $2.0\times$ | **1.25** | **+2.8R** | **+0.04R** | $10.9\text{ bars}$ | **PASS** |
| **EURGBP** | **BUY** | 28 | 15 / 13 | **54%** | $65\text{p} / 52\text{p}$ | $2.0\times$ | **1.25** | **+6.2R** | **+0.22R** | $12.3\text{ bars}$ | **PASS** |
| **EURJPY** | **BUY** | 120 | 72 / 48 | **60%** | $110\text{p} / 88\text{p}$ | $2.0\times$ | **1.25** | **+43.3R** | **+0.36R** | $12.2\text{ bars}$ | **PASS** |
| **GBPJPY** | **BUY** | 34 | 22 / 12 | **65%** | $125\text{p} / 100\text{p}$ | $2.0\times$ | **1.25** | **+14.1R** | **+0.41R** | $11.9\text{ bars}$ | **PASS** |
| **GBPUSD** | **BUY** | 37 | 19 / 18 | **51%** | $86\text{p} / 69\text{p}$ | $2.0\times$ | **1.25** | **+5.9R** | **+0.16R** | $10.7\text{ bars}$ | **PASS** |
| **USDCHF** | **SELL** | 40 | 24 / 16 | **60%** | $62\text{p} / 49\text{p}$ | $2.0\times$ | **1.25** | **+10.9R** | **+0.27R** | $12.4\text{ bars}$ | **PASS** |
| **USDJPY** | **BUY** | 140 | 78 / 62 | **56%** | $109\text{p} / 87\text{p}$ | $2.0\times$ | **1.25** | **+24.2R** | **+0.17R** | $12.2\text{ bars}$ | **PASS** |

### Combined Portfolio Synthesis:
- **Total Codified Setups**: **16 active setups** (8 MSD + 8 PYS)
- **Cumulative Net Profit**: **$+170.5R$** ($+33.4R$ MSD + $+137.1R$ PYS)
- **Average Mathematical Expectancy**: **$+0.231R\text{ per trade}$** across 738 verified decadal occurrences
- **Portfolio Win Rate**: **$57.2\%$**

---

## 5. Multi-Method Quantitative Factor Taxonomy

FMS models macro trading across **Major Forex Extended** through 5 distinct quantitative methods:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FMS MULTI-METHOD TAXONOMY                       │
├────────────────────────────────────────────────────────────────────────┤
│ Method 1: [M-MSD] Macro Surprise Divergence (PACD) [ACTIVE - 8 SETUPS] │
│ • Rolling standardized surprise vector spread between two G8 currencies│
│ • S&R Zone Confluence + ATR Dynamic Volatility Scaling (+33.4R).       │
├────────────────────────────────────────────────────────────────────────┤
│ Method 2: [M-PYS] Policy & Real Yield Spread Momentum [ACTIVE - 8 SETUPS]│
│ • Central bank rate divergence & Irving Fisher Real Yield Spreads.     │
│ • S&R Zone Confluence + Multi-Week Drift Acceleration (+137.1R).       │
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
│ • Microstructure order-flow model for news fakeouts at H4/D1 zones.   │
│ • Exploits institutional absorption of late retail breakout buyers.    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Directory Layout & Isolated Architecture

```
fms/
├── pyproject.toml              # Dependencies (polars, numpy, fastapi, uvicorn, typer, rich)
├── run_dev.py                  # Standalone local dev runner (port 8002)
├── README.MD                   # Master FMS documentation (this file)
├── data/                       # Local compressed caches & SQLite store (gitignored)
│   ├── cache/                  # Parquet candle & calendar historical caches (166k bars)
│   └── fms_store.db            # SQLite: Registered setups, active trades, journal ledger
├── tests/                      # Unit test suite (pytest)
│   └── test_fms_analytics.py   # 5 automated tests
└── src/
    └── fms_engine/
        ├── config.py           # Paths, ports, ATR/MAE/MFE parameters
        ├── contracts/          # Shared Pydantic models (events, setups, trades, journal)
        │   ├── event_models.py
        │   ├── setup_models.py
        │   └── journal_models.py
        ├── ingestion/          # Bridge client, candle loader, calendar loader (Parquet caching)
        │   ├── bridge_client.py
        │   ├── candle_loader.py
        │   └── calendar_loader.py
        ├── analytics/          # Pure quantitative calculations
        │   ├── surprise_engine.py         # Z-score standardization & 4 Macro Reaction States
        │   ├── zone_detector.py           # 2D S&R liquidity box generator (swing pivots + ATR buffer)
        │   ├── excursion_engine.py        # ATR-normalized MAE/MFE survival simulation
        │   └── macro_divergence_engine.py # [M-MSD] 10-year multi-pair divergence cruncher
        ├── strategy/           # Setup registry, trade tracker, journal ledger
        │   ├── setup_registry.py
        │   ├── trade_tracker.py
        │   └── journal_ledger.py
        ├── api/                # FastAPI service & Web Portal
        │   ├── app.py          # Routes for setups, trades, signals, journal, and portal
        │   └── portal_html.py  # Self-contained dark-themed Knowledge & Strategy Portal
        └── cli/                # Standalone CLI research workbench
            └── main.py
```

---

## 7. Verification Commands

Always run these commands before submitting changes:
```powershell
# Run FMS test suite (5 passed)
.\fms\.venv\Scripts\pytest.exe fms\tests

# Verify Python syntax and imports
.\fms\.venv\Scripts\python.exe -m compileall fms\src
```
