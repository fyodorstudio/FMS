# Fyodor repository rules

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
