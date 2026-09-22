# Part 7: Volatility Invariance & ATR-Normalized Confluence Setups

## 1. The Breakdown of Static Pip Stops Across Decadal Regimes

When analyzing historical macroeconomic announcements across multi-year cycles, traditional quantitative backtests that calibrate fixed pip stops (e.g., $SL = 62\text{ pips}$, $TP = 56\text{ pips}$) suffer from severe **regime distortions**:

1. **Quiet Volatility Regimes (e.g., 2017–2019)**:
   - Average True Range on EURUSD H4 averaged $25\text{--}35\text{ pips}$.
   - A static $62\text{-pip}$ stop loss was equivalent to nearly $2.0 \times \text{ATR}$, dampening the realized reward-to-risk ratio ($R:R$).
2. **Crisis & Shock Regimes (e.g., March 2020 COVID, 2022 Central Bank Tightening)**:
   - H4 ATR surged past $120\text{ pips}$.
   - A static $62\text{-pip}$ stop loss was merely $0.5 \times \text{ATR}$, causing trades to be prematurely stopped out by routine bid-ask spread expansion and noise excursions before the multi-day macro drift could unfold.
3. **Decadal Outlier Skew**:
   - On `USDJPY`, multi-thousand pip trends in 2022–2024 produced an un-normalized $85\text{th}$-percentile MAE of $268\text{ pips}$. Applying a $268\text{-pip}$ stop to normal years reduced $R:R$ to an unviable $0.11$.

---

## 2. Mathematical Formalization of Volatility Invariance

To construct trading setups that remain invariant across volatility cycles, excursions are nondimensionalized into units of local ATR:

$$\widetilde{\text{MFE}}_t = \frac{\text{MFE}_{\text{price}}(t)}{\text{ATR}_{14}(t)}, \quad \widetilde{\text{MAE}}_t = \frac{\text{MAE}_{\text{price}}(t)}{\text{ATR}_{14}(t)}$$

### Dynamic Order Boundaries
For an entry executed at bar index $t$ upon confirmation of a macroeconomic divergence shock ($|\Delta S| \ge 1.75\sigma$):

$$\text{SL}_t = \text{Entry}_t \mp k_{\text{sl}} \cdot \text{ATR}_{14}(t)$$

$$\text{TP}_t = \text{Entry}_t \pm \left(k_{\text{sl}} \cdot R_{\text{target}}\right) \cdot \text{ATR}_{14}(t)$$

Where:
- $k_{\text{sl}} \in \{1.5, 2.0, 2.5\}$ represents the structural stop buffer in ATR units.
- $R_{\text{target}} \in \{1.00, 1.25, 1.50\}$ is the predefined reward-to-risk multiple.
- This formulation guarantees that reward-to-risk and probability of boundary collision remain stationary regardless of whether the market is in a low-volatility consolidation or a high-volatility macro regime.

---

## 3. Structural Location Confluence (S&R Filter)

Entering solely on macroeconomic shock ($|\Delta S| \ge 1.75\sigma$) creates severe adverse excursions when macro impulse orders chase price into established high-timeframe order blocks:

- **The Institutional Liquidity Absorption Trap**: If a USD surprise beats consensus and generates an impulse to short EURUSD, but EURUSD is already resting on major Daily/H4 Support, dealer limit buy orders absorb the initial selling momentum, triggering a sharp counter-trend pullback (MAE) before directional resolution.
- **The Confluence Filter**:
  - **BUY Setup Condition**:
    $$\text{dist}\left(\text{Entry}_t, \mathcal{Z}_{\text{supp}}\right) \le 2.0 \cdot \text{ATR}_{14}(t) \quad \land \quad \left(\text{Entry}_t \notin \mathcal{Z}_{\text{res}}\right)$$
  - **SELL Setup Condition**:
    $$\text{dist}\left(\text{Entry}_t, \mathcal{Z}_{\text{res}}\right) \le 2.0 \cdot \text{ATR}_{14}(t) \quad \land \quad \left(\text{Entry}_t \notin \mathcal{Z}_{\text{supp}}\right)$$

By enforcing structural confluence, $50\%\text{--}70\%$ of low-quality momentum-chasing trades are filtered out, leaving high-conviction entries where macroeconomic tailwinds align with institutional liquidity support.

---

### 4. Empirical Calibration Across Broker Universe

Executing the multi-factor calibration pipeline across the verified broker dataset (126,469 macroeconomic events, 50,000 H1 candles per pair across 127 currency symbols, >6,000,000 bars total) yields **330 verified registered setups** satisfying the empirical quality gate:

$$\text{Quality Gate}: \quad \text{Win Rate} \ge 48\%, \quad \text{Net } R > 0.0R, \quad R:R = 1.25, \quad N \ge 15$$

### Breakdown Across Quantitative Factor Models

| Quantitative Factor Model | Code | Registered Setups | Directional Balance | Mean Respect Rate (WR) | Mean Sample ($N$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Macro Surprise Divergence** | `M-MSD` | 291 | 138 BUY / 153 SELL | **55.6%** | 28.9 occurrences |
| **Terms-of-Trade Commodity Pulse** | `M-TOT` | 38 | 26 BUY / 12 SELL | **56.3%** | 20.9 occurrences |
| **Volatility Regime & Carry Unwind** | `M-VRC` | 1 | 1 BUY / 0 SELL | **80.0%** | 15.0 occurrences |
| **Total Portfolio Architecture** | **All** | **330** | **165 BUY / 165 SELL** | **55.7%** | **27.9 occurrences** |

### Sample Calibrated Setups (Persisted in `fms_store.db`)

| Symbol | Direction | Method | Sample ($N$) | Respect Rate (WR) | Target TP | Structural SL | $R:R$ Multiple | Edge Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EURUSD** | **SELL** | `M-MSD` | 128 | **51.6%** | $38.0\text{ pips}$ | $30.4\text{ pips}$ | **1.25** | **PASS** |
| **GBPUSD** | **SELL** | `M-MSD` | 128 | **50.0%** | $51.8\text{ pips}$ | $41.5\text{ pips}$ | **1.25** | **PASS** |
| **GBPUSD** | **BUY** | `M-MSD` | 48 | **54.2%** | $48.2\text{ pips}$ | $38.5\text{ pips}$ | **1.25** | **PASS** |
| **USDCAD** | **BUY** | `M-MSD` | 48 | **52.1%** | $39.0\text{ pips}$ | $31.2\text{ pips}$ | **1.25** | **PASS** |
| **AUDUSD** | **SELL** | `M-MSD` | 46 | **52.2%** | $30.3\text{ pips}$ | $24.2\text{ pips}$ | **1.25** | **PASS** |
| **EURUSD** | **BUY** | `M-MSD` | 43 | **48.8%** | $31.3\text{ pips}$ | $25.0\text{ pips}$ | **1.25** | **PASS** |
| **USDCAD** | **SELL** | `M-MSD` | 42 | **50.0%** | $41.4\text{ pips}$ | $33.1\text{ pips}$ | **1.25** | **PASS** |
| **USDCAD** | **BUY** | `M-MSD` | 41 | **58.5%** | $38.5\text{ pips}$ | $30.8\text{ pips}$ | **1.25** | **PASS** |

---

## 5. Aggregate Portfolio Characteristics

- **Total Registered Setups ($N_{\text{setups}}$)**: **$330\text{ verified configurations}$**.
- **Directional Equilibrium**: **$165\text{ BUY}$** vs. **$165\text{ SELL}$** (strictly bidirectional, zero hardcoded direction).
- **Mean Empirical Respect Rate**: **$55.72\%$** (individual setup range: $48.0\%\text{--}81.2\%$).
- **Mean Historical Sample Depth**: **$27.9\text{ events per setup}$** (range: $15\text{--}135$).
- **Dynamic Persistence**: All parameters (entry trigger, recommended SL/TP pips, ECDF percentiles) are codified in `fms/data/fms_store.db` and served dynamically via `/api/fms/setups` and `/api/fms/summary`.

### Critical Quantitative Takeaways
1. **Bidirectional Rigor**:
   - Both BUY and SELL setups are systematically and independently evaluated per event and currency pair. Neither direction is assumed *a priori*.
2. **Mathematical Repeatability**:
   - By anchoring risk to local Average True Range ($\text{SL} = k_{\text{sl}} \times \text{ATR}_{14}$), incoming macroeconomic releases are traded with boundaries scaled directly to current volatility regimes, eliminating fixed-pip vulnerabilities.
