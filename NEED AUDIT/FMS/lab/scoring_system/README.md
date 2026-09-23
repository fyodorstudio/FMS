# FMS Macroeconomic Scoring Engine (Surprise & Momentum)

A 100% deterministic mathematical scoring engine for macroeconomic event releases based on **Actual vs. Forecast vs. Previous (A/F/P)**.

---

## 1. Mathematical Formulas

### A. Raw Expectation Shock (Surprise)
$$\Delta S = \text{Actual} - \text{Forecast}$$

Measures how much the data diverged from consensus Wall Street expectations.

### B. Raw Trend Shock (Momentum)
$$\Delta M = \text{Actual} - \text{Previous}$$

Measures whether the underlying macroeconomic indicator is expanding or contracting relative to the prior period.

### C. Standardized Volatility-Scaled Z-Score
$$Z = \frac{\Delta S}{\sigma_{\text{event}}}$$

Where $\sigma_{\text{event}}$ is the empirical sample standard deviation of historical forecast errors:
$$\sigma_{\text{event}} = \sqrt{\frac{1}{N - 1} \sum_{i=1}^{N} (\Delta S_i - \overline{\Delta S})^2}$$

### D. Inverted Indicator Handling
For metrics where a higher number represents economic deterioration (e.g., **Unemployment Rate**, **Initial Jobless Claims**, **Claimant Count**):
$$Z_{\text{effective}} = -1.0 \times Z, \quad \Delta M_{\text{effective}} = -1.0 \times \Delta M$$

This guarantees that **positive $Z$ and positive Momentum always represent an economic tailwind (bullish pressure) for the domestic currency**.

---

## 2. The 4-Quadrant Macro State Matrix

| Macro State | Mathematical Condition | Market Meaning |
| :--- | :--- | :--- |
| **`FULL_ACCELERATION`** | $Z > +0.25$ **and** $\Delta M > 0$ | **Strong Beat**: Beat consensus expectations and expanded above previous print. High-conviction bullish catalyst. |
| **`FULL_DECELERATION`** | $Z < -0.25$ **and** $\Delta M < 0$ | **Strong Miss**: Missed consensus expectations and contracted below previous print. High-conviction bearish catalyst. |
| **`CONFLICTED`** | $(Z > +0.25 \land \Delta M < 0)$ or $(Z < -0.25 \land \Delta M > 0)$ | **Divergent Shock**: Beat forecast but lower than previous (or missed forecast but higher than previous). Choppy, mean-reverting price action. |
| **`IN_LINE`** | $|Z| \le 0.25$ | **Within Consensus Noise Band**: Market usually fades initial spike and reverts to prevailing technical trend. |

---

## 3. Running Unit Tests
```powershell
python -m unittest FMS/scoring_system/test_scoring_engine.py
```
Zero synthetic data, zero external dependencies. Pure standard library Python.
