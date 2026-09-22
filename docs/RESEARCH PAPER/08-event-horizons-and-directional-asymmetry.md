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

Analyzing the 10-year dataset (1,847 events, 2017–2026) across EUR/USD, GBP/USD, and AUD/USD reveals distinct empirical peak excursion bars ($\tau_{\text{peak}}$):

| Event Family | Sample ($N$) | Median Peak Bar ($\tau_{\text{peak}}$) | Calendar Duration | $75\text{th}$ Percentile | Microstructure Transmission Mechanism |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Central Bank & Rates** | 153 | **28.0 bars** | $\approx 4.7\text{ days}$ | $33.0\text{ bars}$ | Shifts 2Y/10Y sovereign yield curves and institutional interest rate swap books. |
| **Inflation (CPI / PCE)** | 231 | **26.0 bars** | $\approx 4.3\text{ days}$ | $32.0\text{ bars}$ | Reprices central bank terminal rate expectations and real bond yields. |
| **Labor & Employment** | 230 | **27.0 bars** | $\approx 4.5\text{ days}$ | $32.8\text{ bars}$ | Serves as the primary growth and wage-pressure pulse for monetary reaction functions. |
| **Sentiment & PMIs** | 230 | **25.0 bars** | $\approx 4.2\text{ days}$ | $32.0\text{ bars}$ | High-frequency survey data with faster mean-reversion and shorter drift half-life. |

### The "Different Medicine for Different Diseases" Principle:
- **Central Bank & Inflation Shocks**: Warrant holding up to **28 H4 bars** because institutional asset reallocations require multiple daily fixing sessions to fully execute.
- **Sentiment & Flash PMIs**: Peak faster at **20&ndash;24 H4 bars** and should be closed earlier before survey noise mean-reverts.

---

## 2. The Microstructure of Directional Asymmetry

When running the 10-year decadal audit across all 24 currency combinations, a striking directional disparity emerges:

$$\mathbf{Short\;USD\;Setups} \gg \mathbf{Long\;USD\;Setups}$$

| Pair | Long Setup Performance | Short Setup Performance | Net Disparity |
| :--- | :---: | :---: | :---: |
| **EURUSD** | **BUY (Short USD)**: Win 56%, **+6.5R**, EV **+0.41R** | **SELL (Long USD)**: Win 47%, +0.1R, EV +0.01R | **+6.4R Advantage to Short USD** |
| **GBPUSD** | **BUY (Short USD)**: Win 64%, **+7.5R**, EV **+0.34R** | **SELL (Long USD)**: Win 37%, -0.2R, EV -0.01R | **+7.7R Advantage to Short USD** |
| **USDJPY** | **SELL (Short USD)**: Win 60%, **+4.3R**, EV **+0.29R** | **BUY (Long USD)**: Win 25%, -3.4R, EV -0.42R | **+7.7R Advantage to Short USD** |
| **AUDUSD** | **BUY (Short USD)**: Win 58%, **+6.6R**, EV **+0.35R** | **SELL (Long USD)**: Win 53%, +0.4R, EV +0.02R | **+6.2R Advantage to Short USD** |
| **USDCAD** | **SELL (Short USD)**: Win 50%, **+2.1R**, EV **+0.12R** | **BUY (Long USD)**: Win 43%, -0.7R, EV -0.10R | **+2.8R Advantage to Short USD** |
| **USDCHF** | **SELL (Short USD)**: Win 58%, **+2.0R**, EV **+0.17R** | **BUY (Long USD)**: Win 14%, -4.8R, EV -0.69R | **+6.8R Advantage to Short USD** |
| **NZDUSD** | **BUY (Short USD)**: Win 70%, **+4.0R**, EV **+0.40R** | **SELL (Long USD)**: Win 29%, -2.4R, EV -0.34R | **+6.4R Advantage to Short USD** |

---

### 3. Why Long USD Trades Fail While Short USD Trades Flourish

1. **Central Bank Currency Intervention (Asymmetric Tail Risk)**:
   - When the US Dollar rallies sharply due to US economic strength, foreign currencies experience severe depreciation. This causes imported inflation for economies like Japan, Switzerland, the Eurozone, and the UK.
   - Consequently, foreign monetary authorities intervene unilaterally:
     - **Bank of Japan (BoJ)**: Carried out massive multi-billion dollar interventions in September/October 2022 and April/July 2024, dumping US Treasuries to buy Yen. A single intervention candle erased 400–600 pips in hours, instantly destroying Long USDJPY setups.
     - **Swiss National Bank (SNB)**: Actively sells foreign exchange reserves to maintain a strong Franc and curb domestic inflation, creating a structural barrier against Long USDCHF.
2. **Global Reserve Rebalancing (The Anti-Dollar Flow)**:
   - The US Dollar represents ~58% of global central bank foreign exchange reserves. When the Dollar becomes overextended, global central banks and sovereign wealth funds systematically rebalance by selling USD and buying G8 alternatives.
3. **Retail Crowding & Liquidity Traps**:
   - Retail participants disproportionately chase bullish USD headlines ("The Fed will stay higher for longer!"). Institutional market makers utilize this retail buying liquidity to unload large short positions, producing counter-trend whipsaws that trigger stop losses on Long USD trades.

### Production Conclusion:
**Symmetrical quantitative trading is an expensive fallacy.** A robust macro framework must restrict trade generation strictly to asymmetric setups where macroeconomic surprise direction aligns with institutional central bank policy incentives.
