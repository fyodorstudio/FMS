# Part 2: Structural Risk Calibration & Excursions

## 1. Maximum Adverse & Favorable Excursions (MAE / MFE)

For each historical occurrence $i \in \{1, \dots, N\}$ of event $E$, let $P_0$ be reference entry price:

$$\text{MFE}_i = \max_{t \in [t_0, t_0 + T]} \left[ \operatorname{dir} \cdot (P(t) - P_0) \right]$$
$$\text{MAE}_i = \max_{t \in [t_0, t_0 + T]} \left[ -\operatorname{dir} \cdot (P(t) - P_0) \right]$$

## 2. ATR Volatility Normalization

To ensure pip measurements are invariant across different market volatility regimes (e.g. low-volatility 2018 vs. high-volatility 2020/2022), excursions are normalized by the 14-period Average True Range ($\text{ATR}_{14}$):

$$\widetilde{\text{MAE}}_i = \frac{\text{MAE}_i}{\text{ATR}_{14}(t_0)}, \quad \widetilde{\text{MFE}}_i = \frac{\text{MFE}_i}{\text{ATR}_{14}(t_0)}$$

## 3. Statistical Level Calibration
- **Stop Loss ($\text{SL}$)**: Fixed at the **85th percentile of normalized MAE** observed in winning moves $+ 0.20 \times \text{ATR}$ buffer:
  $$\text{SL} = P_0 - \operatorname{dir} \cdot \left( \mathcal{Q}_{0.85}(\widetilde{\text{MAE}}_{\text{wins}}) + 0.20 \right) \times \text{ATR}_{14}$$
- **Take Profit ($\text{TP}$)**: Fixed at the **median normalized MFE (50th percentile)**:
  $$\text{TP} = P_0 + \operatorname{dir} \cdot \mathcal{Q}_{0.50}(\widetilde{\text{MFE}}_{\text{all}}) \times \text{ATR}_{14}$$
- **Expectancy Filter**: Any setup yielding statistical $R:R < 1.30$ or Respect Rate $< 65\%$ is suppressed.

## 4. 2-Dimensional Liquidity Zones (Support & Resistance)

S&R levels are modeled as **liquidity boxes** rather than 1D price lines:
- **Resistance Zone $\mathcal{Z}_{\text{res}}$**: $[\max(\text{Close}, \text{High} - 0.25 \times \text{ATR}), \; \text{High}]$
- **Support Zone $\mathcal{Z}_{\text{sup}}$**: $[\text{Low}, \; \min(\text{Close}, \text{Low} + 0.25 \times \text{ATR})]$

**Confluence Requirement**: A macro sell signal is prioritized when price currently trades within or rejects an $H4/D1$ Resistance Zone, minimizing initial drawdown (MAE).

## 5. Mitigating the Curse of Macro Dimensionality

Group scarce individual releases ($N \approx 8\text{--}12/\text{year}$) into **5 Macro Families**:
1. **Monetary Policy**: Central Bank Rate Decisions, Minutes, Forward Guidance.
2. **Inflation**: CPI, Core CPI, PPI, PCE Price Index.
3. **Labor**: Non-Farm Payrolls, Unemployment Rate, Jobless Claims.
4. **Growth**: GDP, Retail Sales, Industrial Production, Trade Balance.
5. **Forward Sentiment**: Manufacturing / Services PMI, ZEW, Consumer Sentiment.
