from __future__ import annotations

from typing import Any


TIMEFRAME_NAMES = {
    "M1": "TIMEFRAME_M1",
    "M5": "TIMEFRAME_M5",
    "M15": "TIMEFRAME_M15",
    "M30": "TIMEFRAME_M30",
    "H1": "TIMEFRAME_H1",
    "H4": "TIMEFRAME_H4",
    "D1": "TIMEFRAME_D1",
}


def _last_error(mt5: Any, prefix: str) -> RuntimeError:
    try:
        code, description = mt5.last_error()
        return RuntimeError(f"{prefix}: [{code}] {description}")
    except Exception:
        return RuntimeError(prefix)


def read_market_watch(mt5: Any) -> list[dict[str, object]]:
    symbols = mt5.symbols_get()
    if symbols is None:
        raise _last_error(mt5, "Unable to read Market Watch")

    rows: list[dict[str, object]] = []
    for symbol in symbols:
        if not bool(getattr(symbol, "visible", False)):
            continue
        bid = float(getattr(symbol, "bid", 0.0) or 0.0)
        ask = float(getattr(symbol, "ask", 0.0) or 0.0)
        session_open = float(getattr(symbol, "session_open", 0.0) or 0.0)
        daily_change = ((bid - session_open) / session_open * 100) if session_open else 0.0
        rows.append(
            {
                "symbol": str(symbol.name),
                "description": str(getattr(symbol, "description", "") or symbol.name),
                "bid": bid,
                "ask": ask,
                "daily_change": daily_change,
                "precision": int(getattr(symbol, "digits", 5) or 5),
            },
        )

    rows.sort(key=lambda row: str(row["symbol"]))
    return rows


def read_ohlc(mt5: Any, symbol: str, timeframe: str, count: int) -> list[dict[str, float | int]]:
    mt5_timeframe_name = TIMEFRAME_NAMES[timeframe]
    mt5_timeframe = getattr(mt5, mt5_timeframe_name)
    if not mt5.symbol_select(symbol, True):
        raise _last_error(mt5, f"Unable to select {symbol}")
    rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
    if rates is None:
        raise _last_error(mt5, f"No {timeframe} history returned for {symbol}")

    bars = [
        {
            "time": int(rate["time"]),
            "open": float(rate["open"]),
            "high": float(rate["high"]),
            "low": float(rate["low"]),
            "close": float(rate["close"]),
            "tick_volume": int(rate["tick_volume"]),
        }
        for rate in rates
    ]
    if not bars:
        raise _last_error(mt5, f"No {timeframe} bars are available for {symbol}")
    return bars
