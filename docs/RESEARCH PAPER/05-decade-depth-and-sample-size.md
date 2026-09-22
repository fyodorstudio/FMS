# Part 5: Decade-Scale Sample Depth & Volatility Regimes

## 1. The Danger of Small-$N$ Statistical Illusions

In short historical evaluations ($< 4$ years), several currency pairs yielded seemingly extraordinary metrics:
- `NZDUSD SELL`: $100\%$ Win Rate, $R:R = 14.32$ ($N = 3$)
- `GBPJPY BUY`: $100\%$ Win Rate, $R:R = 3.63$ ($N = 3$)

In rigorous mathematical statistics, an observation size of $N = 3$ is **statistically ungrounded**:
- Standard error of a Bernoulli trial proportion:
  $$\text{SE}(p) = \sqrt{\frac{p(1 - p)}{N}}$$
  At $N = 3$, the $95\%$ confidence interval for a $100\%$ observed win rate spans $[29.2\%, \; 100\%]$—rendering the metric clinically useless for risk-budgeting.

---

## 2. Decade-Scale Expansion (2017–2026)

By pulling **15,000 H4 bars** across all 12 pairs in Major Forex Extended (**166,283 candles total**), sample frequency $N$ expanded to **$25\text{--}35$ independent events per direction ($50\text{--}70$ per pair)**:
- Satisfies the asymptotic normality requirements of the Central Limit Theorem:
  $$\sqrt{N} (\hat{p} - p) \xrightarrow{d} \mathcal{N}\left(0, \; p(1 - p)\right)$$
- Win rates held solid across 10 years:
  - `USDCAD SELL`: **64%** over 25 independent macro trades
  - `GBPUSD SELL`: **60%** over 35 independent macro trades
  - `AUDUSD SELL`: **58%** over 33 independent macro trades

---

## 3. The Multi-Year Volatility Regime Trap

Expanding to 10 years revealed a critical structural lesson:
- **Raw-Pip MAE Blowout**: In the 10-year test, static 85th-percentile MAE expanded to $200\text{--}260\text{ pips}$.
- **Root Cause**: The 10-year window includes extreme volatility regimes:
  - 2020 Pandemic Liquidity Shock (Daily range $> 180\text{ pips}$)
  - 2022 Ukraine / Global Inflation Shock (Daily range $> 150\text{ pips}$)
  - 2017–2019 Quiet Secular Grind (Daily range $\approx 45\text{ pips}$)
- When measuring in static pips, a single high-volatility event in 2020 corrupts the 85th percentile for the entire decade, forcing an oversized stop loss on quiet periods.

**Resolution**: Excursions must be calibrated in **units of entry-time ATR** ($\widetilde{\text{MAE}} = \text{MAE} / \text{ATR}_{14}$), allowing stop-loss and take-profit levels to scale dynamically with the prevailing volatility regime.

---

## 4. Negative Empirical Findings: Why Blind News Fails on Majors

- `EURUSD`, `GBPUSD`, and `USDJPY` are the primary execution ground for multi-bank high-frequency algorithmic liquidity sweeps. 
- Adverse excursions regularly reach $200\text{--}300\text{ pips}$ during news releases, yielding poor un-filtered $R:R$ ($0.30\text{--}0.50$).
- *The Asymmetric Exception*: Commodity-linked currencies (`AUDUSD`, `NZDUSD`) exhibited far cleaner directional drift and tighter MAE distributions, as physical export supply-demand fundamentals override speculative intraday churn.
