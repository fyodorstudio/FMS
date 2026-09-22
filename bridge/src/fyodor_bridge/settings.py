from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BridgeSettings:
    mt5_terminal_path: str | None
    mt5_call_timeout_seconds: float
    mt5_status_interval_seconds: float
    allowed_origins: tuple[str, ...]


def load_settings() -> BridgeSettings:
    configured_path = os.getenv("FYODOR_MT5_TERMINAL_PATH", "").strip()
    return BridgeSettings(
        mt5_terminal_path=configured_path or None,
        mt5_call_timeout_seconds=float(os.getenv("FYODOR_MT5_CALL_TIMEOUT_SECONDS", "30.0")),
        mt5_status_interval_seconds=2.0,
        allowed_origins=("http://127.0.0.1:5173", "http://localhost:5173"),
    )
