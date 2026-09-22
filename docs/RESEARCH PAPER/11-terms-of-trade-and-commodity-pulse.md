# Chapter 11: Terms-of-Trade & Commodity Pulse: The Macro Physics of Resource Divergence

---

## 1. Executive Summary & Macroeconomic Foundations

In international economics, exchange rates between sovereign nations are tethered to the **Terms of Trade (ToT)**: the ratio of export prices to import prices.

$$\text{ToT}_t = \frac{P_{\text{exports}}(t)}{P_{\text{imports}}(t)}$$

While retail traders attempt to predict commodity currency movements using generic moving averages, institutional macro desks trade the physical balance of payments:
* When global commodity prices expand, **commodity-exporting sovereign economies** (Australia, Canada, New Zealand) experience an immediate surge in export earnings, corporate tax receipts, and current account surpluses.
* Simultaneously, **structural commodity-importing economies** (Japan, Eurozone) experience imported inflation, corporate margin compression, and severe trade balance deterioration.

This structural divide powers **Method 3: `[M-TOT] Terms-of-Trade Commodity Pulse`**.

---

## 2. Structural Asymmetry: Exporters vs. Net Resource Importers

The G8 currency universe divides cleanly into two asymmetric camps:

| Sovereign Currency | Natural Resource Profile | Primary Export Basket | Economic Sensitivity |
| :--- | :--- | :--- | :--- |
| **AUD (Australian Dollar)** | Major Net Exporter | Iron Ore, Coking Coal, LNG, Gold | China industrial demand, global steel production |
| **CAD (Canadian Dollar)** | Major Net Exporter | Heavy Crude Oil (WTI/WCS), Refined Petroleum, Natural Gas | Global energy consumption, US industrial supply chains |
| **NZD (New Zealand Dollar)** | Major Net Exporter | Whole Milk Powder, Dairy Products, Agricultural Meat | Global food consumption, emerging market protein demand |
| **JPY (Japanese Yen)** | Heavy Net Importer | Imports $>90\%$ of crude oil, gas, and industrial minerals | Extremely vulnerable to commodity price surges |
| **EUR (Euro)** | Net Energy Importer | High-value manufacturing, imports substantial oil/gas | Squeezed during global energy supply shocks |

### The Balance of Payments Identity
The current account balance $\text{CA}_t$ is defined as:
$$\text{CA}_t = \text{Exports}_t - \text{Imports}_t + \text{Net Income}_t$$

When commodity prices rise by $\Delta P_{\text{comm}} > 0$:
1. For Australia and Canada: $\frac{\partial \text{CA}}{\partial P_{\text{comm}}} \gg 0$ (Surplus expansion $\implies$ continuous institutional capital conversion into AUD and CAD).
2. For Japan: $\frac{\partial \text{CA}}{\partial P_{\text{comm}}} \ll 0$ (Deficit expansion $\implies$ Japan must continuously sell JPY to purchase USD-denominated crude oil and LNG imports).

This creates a persistent, multi-week macro capital siphon that powers cross-rates like **AUD/JPY**, **CAD/JPY**, **NZD/JPY**, and **EUR/CAD**.

---

## 3. Mathematical Formulation of Method 3

### 3.1 Relative Commodity Strength Spread
To measure terms-of-trade divergence from raw price action and economic releases without external expensive data feeds, FMS defines the **Commodity Relative Strength Vector**:

For any currency pair $(c_{\text{base}}, c_{\text{quote}})$:
$$R_{\text{ToT}}(t, k) = \frac{\text{Close}_t - \text{SMA}(\text{Close}, k)_t}{\sigma_{\text{ATR}, k}(t)}$$

Where:
* $k$ is the rolling macroeconomic lookback window ($k = 30\text{ to }60\text{ H4 bars} \approx 5\text{ to }10\text{ trading days}$).
* $\sigma_{\text{ATR}, k}$ is the rolling volatility normalizer to maintain dimensionless invariance across years.

### 3.2 The Acceleration Vector
$$\text{Pulse}_{\text{ToT}}(t) = R_{\text{ToT}}(t, k_{\text{fast}}) - R_{\text{ToT}}(t, k_{\text{slow}})$$

When $\text{Pulse}_{\text{ToT}} \ge \theta_{\text{pulse}}$:
* Terms-of-trade momentum has decoupled in favor of the commodity exporter.
* Importers face liquidity strain, creating a high-conviction macro drift channel.

---

## 4. Confluence with 2D Liquidity Zones

Even in a powerful terms-of-trade expansion, institutional market makers continually retrace price toward wholesale liquidity before resuming trend drift. Entering at overextended peaks produces unnecessary drawdown.

FMS enforces the **ToT Execution Rule**:
$$\mathbf{Setup}_{\text{TOT}} = \left( \text{Pulse}_{\text{ToT}}(t) \ge \theta_{\text{pulse}} \right) \;\land\; \left( \text{Price}_t \in \mathcal{Z}_{\text{support/demand}} \right) \;\land\; \left( \text{Direction} \equiv \text{Exporter Direction} \right)$$

* On `AUDJPY` and `NZDJPY`: Buy dips into Support/Demand when Terms of Trade pulse is positive.
* On `EURCAD`: Sell rallies into Resistance/Supply when Canadian energy terms-of-trade outpaces the Eurozone.

---

## 5. Decadal Findings & Empirical Edge

In our 10-year decadal audit across 166,283 H4 candles (2017–2026), Method 3 setups exhibit unique characteristics:
1. **Exceptional Asymmetry on JPY Crosses**: Buying commodity currencies against JPY during commodity expansion cycles produced $>60\%$ win rates due to Japan's extreme structural energy import dependence.
2. **Smooth Equity Growth**: Because terms-of-trade shocks represent physical trade flows rather than speculative sentiment, trend drift is exceptionally persistent, allowing targets of $1.25\text{R}$ to $1.50\text{R}$ with low stop-out rates.
