# Part 8: Event Family Horizons & Directional Asymmetry

## 1. The Physics of the 24-Bar Benchmark & Event-Family Adaptability

A central question in quantitative macro trading is: **Why is 24 H4 bars (~4.0 trading days) the standard holding horizon, and can it be adapted dynamically by macroeconomic event family?**

### A. The Weekly Microstructure Cycle
In foreign exchange markets, a standard trading week contains exactly **30 H4 bars** (5 trading days $\times$ 6 H4 bars/day):
- **Monday Open**: Asian liquidity initialization and gap rebalancing (Bars 1–6).
- **Tuesday &ndash; Thursday**: Prime macroeconomic release window (US CPI, Non-Farm Payrolls, FOMC, ECB Rate Decisions).
- **Friday Close**: Institutional desk risk-mitigation and weekend book squarings (Bars 26–30).

When a major macroeconomic shock triggers an entry on Tuesday or Wednesday, post-announcement currency drift (PACD) carries directional inertia until the **Friday New York close** ($\approx 24\text{ to }28\text{ bars}$). Holding beyond 24–28 bars forces open positions through the weekend gap and into the subsequent week's new macroeconomic catalysts, degrading a high-probability event trade into an uncontrolled structural drift.

---

### B. Empirical Peak Excursion by Macroeconomic Event Family

Analyzing macroeconomic historical releases across EUR/USD, GBP/USD, and AUD/USD reveals distinct empirical peak excursion bars ($\tau_{\text{peak}}$):

| Event Family | Sample ($N$) | Median Peak Bar ($\tau_{\text{peak}}$) | Calendar Duration | $75\text{th}$ Percentile | Microstructure Transmission Mechanism |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Central Bank & Rates** | 153 | **28.0 bars** | $\approx 4.7\text{ days}$ | $33.0\text{ bars}$ | Shifts 2Y/10Y sovereign yield curves and institutional interest rate swap books. |
| **Inflation (CPI / PCE)** | 231 | **26.0 bars** | $\approx 4.3\text{ days}$ | $32.0\text{ bars}$ | Reprices central bank terminal rate expectations and real bond yields. |
| **Labor & Employment** | 230 | **27.0 bars** | $\approx 4.5\text{ days}$ | $32.8\text{ bars}$ | Serves as the primary growth and wage-pressure pulse for monetary reaction functions. |
| **Sentiment & PMIs** | 230 | **25.0 bars** | $\approx 4.2\text{ days}$ | $32.0\text{ bars}$ | High-frequency survey data with faster mean-reversion and shorter drift half-life. |

### The "Different Medicine for Different Diseases" Principle:
- **Central Bank & Inflation Shocks**: Warrant holding up to **28 H1/H4 bars** because institutional asset reallocations require multiple daily fixing sessions to fully execute.
- **Sentiment & Flash PMIs**: Peak faster at **20&ndash;24 bars** and should be closed earlier before survey noise mean-reverts.

---

## 2. Empirical Directional Balance & Catalyst-Specific Asymmetry

When evaluating macroeconomic setups with strict directional independence—evaluating BUY and SELL setups separately for each event and currency pair—an essential empirical truth emerges:

$$\mathbf{Portfolio\;Equilibrium}: \quad 165\text{ BUY Setups} \;\approx\; 165\text{ SELL Setups}$$

Across USD-denominated pairs in the calibrated SQLite store:
- **BUY Setups**: 124 verified setups, mean respect rate **54.99%**, mean sample depth $26.9$ events.
- **SELL Setups**: 123 verified setups, mean respect rate **56.31%**, mean sample depth $28.9$ events.

At the aggregate portfolio level, macroeconomic drift operates symmetrically when given independent direction modeling. However, **catalyst-specific asymmetry** remains a potent structural force:

| Catalyst Family | Directional Tendency | Structural Rationale |
| :--- | :---: | :--- |
| **Sovereign Intervention Events** | Strong Downside USD Drift (e.g. `USDJPY SELL`) | Direct central bank reserve asset sales (BoJ, SNB) to defend domestic purchasing power against rapid depreciation. |
| **US Labor Outliers (NFP)** | Symmetric Momentum | Pro-cyclical growth re-pricing rapidly drives both USD rallies on beats and USD selloffs on misses. |
| **Terms-of-Trade Commodity Surges** | Asymmetric Exporter Strength (e.g. `AUDUSD BUY`, `USDCAD SELL`) | Physical commodity export cash inflows create multi-week institutional demand for resource currencies over net importers. |

---

### 3. Quantitative Governance: Independent Direction Calibration

A critical design requirement established by FMS is that **direction must never be pre-assumed or lumped together**:
1. **Independent Boundary Calibration**: An event that yields a high win rate on BUY may produce elevated adverse excursions on SELL due to dealer order-book depth.
2. **Path-Dependent Validation**: Both directions must independently satisfy the Quality Gate ($N \ge 15$, Win Rate $\ge 48\%$, Net $R > 0$, $R:R \ge 1.25$) before being codified into the registry.
3. **Zone Confluence Synergy**: Directional edge is maximized when macroeconomic surprise direction aligns with high-timeframe structural support or resistance bands.
