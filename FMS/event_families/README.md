# FMS Event Families Explorer (Standalone HTML)

An interactive, self-contained standalone HTML application to explore, sort, and inspect the 5 core Macroeconomic Event Families.

---

## 1. How to Open
Double-click `event_families_explorer.html` or open it with your web browser:

```powershell
start FMS/event_families/event_families_explorer.html
```

- **Zero dependencies**: Pure HTML, CSS, and vanilla JS.
- **100% offline**: Requires no web server, node, or python to run.

---

## 2. Features

1. **Sort by Sample Depth ($N$)**:
   - Click the **Sample (N)** column header to immediately sort from highest $N$ to lowest $N$ (or vice versa).
   - Any column (Event Name, Currency, Family, Historical $\sigma$, Respect Rate, Excursion) can be sorted ascending/descending.
2. **Family & Currency Filters**:
   - Filter by **Monetary Policy**, **Inflation**, **Labor**, **Growth**, or **Sentiment**.
   - Filter by primary currency: `USD`, `EUR`, `GBP`, `JPY`, `AUD`, `CAD`.
3. **Interactive Precedent Dossier**:
   - Click on any row to open the Event Precedent Detail Card.
   - Shows the exact mathematical formula, historical respect rate, inverted indicator logic, and currency pair impact.
