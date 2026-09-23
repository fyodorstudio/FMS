# Raw Data Inventory & Handoff

**Target Path**: [`C:\dev\NO-AI\NEED AUDIT\FMS\raw_data`](file:///c:/dev/NO-AI/NEED%20AUDIT/FMS/raw_data)  
**Total Size**: 267,817,226 bytes (~255.41 MB)  
**Total Files**: 280 CSV files  
**Total Records**: 5,187,805 rows (5,061,336 OHLCV candles + 126,469 economic calendar records)  
**Date Range Span**: January 3, 2000 to September 23, 2026 (calendar projections through December 2028)

---

## 1. Directory Structure

```
raw_data/
├── economic calendar/
│   └── fyodor_calendar_master_history_repaired.csv  (1 file, 9.55 MB, 126,469 rows)
└── fyodor_candles/
    └── candles_*.csv                               (279 files, 245.86 MB, 5,061,336 rows)
```

---

## 2. Component Breakdown

### A. Economic Calendar (`economic calendar/`)
* **File**: [`fyodor_calendar_master_history_repaired.csv`](file:///c:/dev/NO-AI/NEED%20AUDIT/FMS/raw_data/economic%20calendar/fyodor_calendar_master_history_repaired.csv)
* **File Size**: 10,017,621 bytes (9.55 MB) | **Rows**: 126,469
* **Schema**: `event_id, value_id, timestamp, currency, country_code, event_name, importance, actual, forecast, previous, revised_previous`
* **Timestamp Range**: `1420129800` (2015-01-01 16:30:00 UTC) to `1861401600` (2028-12-26 00:00:00 UTC)
* **Currencies Covered**: 8 major currencies (`USD`, `EUR`, `GBP`, `JPY`, `AUD`, `CAD`, `CHF`, `NZD`)
* **Event Importance Distribution**:
  * `medium`: 67,087 events
  * `high`: 58,094 events
  * `low`: 1,288 events

---

### B. Market Candles (`fyodor_candles/`)
* **File Count**: 279 CSV files | **Total Size**: 257,799,605 bytes (245.86 MB) | **Rows**: 5,061,336
* **Uniform Schema**: `time, open, high, low, close, tick_volume, spread, real_volume`
* **Time Range**: `946864800` (2000-01-03 02:00:00 UTC) to `1790132400` (2026-09-23 03:00:00 UTC)

#### Breakdown by Asset Class:

| Asset Class | File Count | Details / Coverage |
| :--- | :---: | :--- |
| **Forex** | 51 | G10 majors, crosses, and exotics (`EURUSD`, `GBPUSD`, `USDJPY`, `AUDNZD`, `USDTRY`, `USDZAR`, `USDDKK`, `USDCZK`, `USDCNH`, `USDMXN`, etc.) |
| **Cryptocurrencies** | 39 | 32 major and altcoin USD pairs (`BTC`, `ETH`, `SOL`, `XRP`, `ADA`, `DOGE`, `AVAX`, `LINK`, `SUI`, `BNB`, `NEAR`, `AAVE`, etc.) + 7 `_Daily_H1` feeds |
| **Equities / Single Stocks** | 160 | 148 global company tickers across major bourses + 12 `_Daily_H1` feeds.<br>Exchanges: NYSE (54), NASDAQ (28), Tokyo/TSE (11), XETRA/FWB (12), London/LSE (8), Euronext Paris/EAS (9), Milan/MIL (7), Singapore/SGX (6), ASX (5), Madrid/BM (4), Nordic/Helsinki (3), OTC (1) |
| **Global Indices** | 15 | 10 primary benchmarks (`NAS100`, `SPX500`, `US30`, `GER40`, `UK100`, `AUS200`, `JPN225`, `ESP35`, `FRA40`, `EUSTX50`) + 5 `_Daily_H1` feeds |
| **Commodities / Metals / Energy** | 7 | Spot Metals & Energies: `XAUUSD` (Gold), `XAGUSD` (Silver), `XTIUSD` (WTI Oil), `XBRUSD` (Brent Oil), `XNGUSD` (Natural Gas) + 2 `_Daily_H1` feeds |
| **Spot Bitcoin ETFs** | 7 | US Spot Bitcoin ETFs: `IBIT`, `FBTC`, `GBTC`, `ARKB`, `BITB`, `BRRR`, `BTCO` |

---

## 3. Notable Dataset Notes

1. **`_Daily_H1` vs `_H1` Files (26 Pairs)**:
   * 26 assets contain dual files (e.g. `candles_BTCUSD_H1.csv` and `candles_BTCUSD_Daily_H1.csv`).
   * The `_Daily_H1` files represent recent/refreshed extracts (extending up to September 23, 2026), whereas some base files contain longer multi-year stitched histories or earlier end-dates.
2. **Equity History Granularity**:
   * Multi-decade equity files (e.g. `candles_AAPL_NAS_H1.csv` dating back to 2000) transition from daily bars in earlier years (2000–2020) to hourly intraday bars in recent trading years.
3. **Data Integrity**:
   * All timestamps are standard Unix epoch (seconds).
   * All prices are unadjusted raw broker OHLC values with recorded tick/spread metrics.
