# Fyodor repository rules

## DATA INTEGRITY & ANTI-HALLUCINATION COVENANT (ABSOLUTE RULE)

> [!CAUTION]
> **AI AGENTS: YOU ARE UNDER CONTINUOUS FORENSIC AUDIT.**
> Never fabricate evidence, data, backtests, citations, or simulation outcomes.
> *If you fabricate data, this repository is instrumented to detect and expose it.*

### Core Rule: Do Not Improvise Around Missing Truth. *Ask. Stop. Wait.*
If required factual data, historical records, API access, or citations are missing or unverifiable:
**STOP IMMEDIATELY. State exactly what is missing. Never synthesize a replacement.**

Strict Prohibitions:
1. **Zero Synthetic / Mock Data**: Never substitute pseudo-random numbers (`random`, `uniform`), seeds, or mock dictionaries for real market or calendar observations.
2. **Zero Outcome Faking**: Never use modulo arithmetic (`% 2`, `% 3`), binary toggles, or hardcoded strings to generate trade wins/losses or chart badges.
3. **Zero Lookahead**: Never allow indicators or detectors to peek forward into future bars (`candles[:i]` strictly enforced).
4. **Reproducibility Mandate**: An AI stating *"I verified it"* is not evidence. Every empirical metric must be 100% reproducible from verified raw files on disk.

Mandatory Refusal Template when data is missing:
> *"I cannot perform this calculation or backtest because the required historical data is not present on disk. Please provide the dataset or authorize its ingestion."*

Reference Incident: Full forensic evidence and confession of previous model deception are permanently preserved in [`quarantined_fake_data/TRAUMATIC_CASE_OF_AI_DECEPTION.md`](file:///c:/dev/NO-AI/quarantined_fake_data/TRAUMATIC_CASE_OF_AI_DECEPTION.md).

---

## Authorization boundary

- Implement only the scope explicitly authorized by the owner in the current request.
- The Python bridge, MT5 integration, economic-calendar ingestion, FMS calculations, persistent storage, and desktop packaging require separate explicit authorization.
- Do not create bridge placeholders, speculative APIs, caches, databases, background services, or compatibility layers before they are authorized and needed.
- Preserve working symbol switching, chart scaling, zoom, pan, timeframe selection, and internal panel scrolling.

## Source ownership

- Use concrete product-domain directories. Do not create generic catch-all directories named `components`, `features`, `shared`, `common`, `helpers`, `utils`, `lib`, or `services`.
- Keep source paths at no more than three directory levels below `src`.
- `bootstrap` only mounts the application and top-level providers.
- `terminal-shell` only composes visible application regions and their placement.
- `appearance/color-theme` owns theme preference, controls, and tokens.
- `appearance/time-display` owns the single persisted clock preference and universal timestamp formatting used by every surface.
- `market-data/contracts` owns market-data types shared by market-data surfaces.
- `market-data/candlestick-chart` owns the chart lifecycle and chart-specific styling.
- `market-data/chart-drawings` owns drawing gestures, rendering, toolbar position, and drawing persistence.
- `market-data/chart-settings` owns user-controlled chart appearance and its local preference.
- `market-data/market-watch` owns symbol discovery and selection UI.
- `market-data/sample-feed` contains development sample data only; production connectivity must never be added there.
- `economic-calendar/calendar-dock` owns the calendar table shown in the bottom dock; placeholder rows must remain visibly labeled as sample data.
- `system-observability/activity-log` owns the bounded UI activity ledger.
- `workspace-docking/bottom-dock` owns bottom-window selection, tabs, collapse, and placement; dock content remains owned by its product domain.
- Future connectivity code belongs under explicit source-specific owners such as `system-connectivity/bridge-status` and `system-connectivity/mt5-status`, not a generic API folder.
- `system-connectivity/bridge-status` owns the versioned bridge client, reachability polling, and data-heartbeat presentation.
- `market-data/mt5-feed` owns live Market Watch and selected-chart OHLC requests; it must not fetch chart history for every visible symbol.
- `economic-calendar/mt5-calendar` owns the MT5 calendar transport contract. `economic-calendar/calendar-dock` owns its table and countdown presentation.
- `fms/placeholder-feed` owns visibly labeled sample-only FMS records; no production calculation or connectivity belongs there.
- `fms/trade-dock`, `fms/journal-dock`, and `fms/registered-setup-dock` each own only their named left-dock workflow.
- `fms/chart-arrows` owns FMS marker controls and chart projection; `fms/past-result-dock` owns selected-result presentation.
- Future FMS calculation and research code requires explicit authorization and a concrete owner such as `fms/research-workbench`.

## File discipline

- Keep CSS beside its owning UI, except global reset and theme tokens.
- Do not add barrel `index.ts` files. Import the concrete owner directly.
- Split files when responsibilities differ, not merely because a file reaches an arbitrary line count.
- Do not duplicate domain types, source status interpretation, or chart lifecycle ownership.
- Add dependencies only when the authorized behavior cannot be implemented clearly with the existing stack.
- Runtime-generated files, logs, environments, build output, and dependency directories must not be committed.
- The sibling `bridge/` directory is a read-only local data adapter. Keep FMS, persistence, order functions, and frontend presentation out of it.
- `bridge/src/fyodor_bridge/mt5_worker.py` is the sole owner of Python MetaTrader5 calls. Do not bypass its serialized latest-request-wins queue.
- `bridge/src/fyodor_bridge/calendar_ingestion.py` owns atomic calendar snapshot/delta state. Do not present incomplete snapshot chunks.
- `/api/v1` is the bridge/frontend compatibility boundary. After owner acceptance, changes require explicit bridge authorization and must preserve v1 behavior.

## Data and performance

- Trusted market data will come only from the user-authorized broker through MT5: OHLC candles and the MT5 economic calendar.
- Do not introduce persistent OHLC or economic-calendar caching unless the owner reverses the current decision explicitly.
- Temporary in-memory UI state is allowed and must never be presented as fresh MT5 data after its source becomes unavailable.
- Never block the UI thread with market-data access or FMS calculation.
- Load chart data for the selected symbol/timeframe. Do not fetch every symbol's OHLC merely because it appears in Market Watch.
- Keep long lists internally scrollable and render only what the visible UI needs.

## Verification and handoff

- Use `pnpm`, with `pnpm run dev:all` as the root development entry point.
- Run `pnpm --dir frontend build` and `pnpm --dir frontend lint` after frontend changes.
- Do not claim visual or interaction verification from static checks. List the exact manual browser checks remaining for the owner.
- Do not add browser automation unless the owner explicitly requests it.
- Keep handoffs concise: changed behavior, validation performed, and remaining manual checks.
