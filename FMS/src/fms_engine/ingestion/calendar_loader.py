from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl
from .bridge_client import BridgeClient
from ..config import settings
from ..contracts.event_models import EventFamily

FAMILY_KEYWORDS = {
    EventFamily.INFLATION: ["cpi", "ppi", "pce", "inflation", "price index"],
    EventFamily.LABOR: ["nfp", "payrolls", "unemployment", "jobless", "employment", "claims", "wages", "labor"],
    EventFamily.MONETARY_POLICY: ["rate decision", "interest rate", "fomc", "ecb", "boe", "rba", "boj", "policy", "statement", "minutes"],
    EventFamily.GROWTH: ["gdp", "retail sales", "industrial production", "trade balance", "orders", "factory"],
    EventFamily.SENTIMENT: ["pmi", "sentiment", "confidence", "zew", "ifo", "ism", "surveys"],
}

def classify_event_family(event_name: str) -> EventFamily:
    lower = event_name.lower()
    for family, keywords in FAMILY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return family
    return EventFamily.GROWTH

class CalendarLoader:
    """Manages ingestion, family categorization, and caching of MT5 economic calendar."""

    def __init__(self, bridge: Optional[BridgeClient] = None):
        self.bridge = bridge or BridgeClient()
        settings.ensure_directories()

    @property
    def cache_path(self) -> Path:
        return settings.cache_dir / "calendar_events.parquet"

    async def sync_calendar(self) -> pl.DataFrame:
        """Fetches calendar from bridge and caches to parquet."""
        data = await self.bridge.get_calendar()
        raw_events = data.get("events", [])
        if not raw_events:
            return self.load_cached_calendar() or pl.DataFrame()

        normalized: List[Dict[str, Any]] = []
        for ev in raw_events:
            name = ev.get("event_name") or ev.get("name") or "Unknown Event"
            family = classify_event_family(name)
            time_val = ev.get("time") or ev.get("timestamp") or 0
            if isinstance(time_val, str):
                try:
                    time_val = int(time_val)
                except ValueError:
                    time_val = 0

            # Convert millisecond timestamps to seconds if necessary
            if time_val > 10_000_000_000:
                time_val //= 1000

            normalized.append({
                "event_id": str(ev.get("event_id") or ev.get("value_id") or ev.get("id") or ""),
                "event_name": name,
                "currency": str(ev.get("currency") or ev.get("country") or "USD"),
                "family": family.value,
                "timestamp": int(time_val),
                "actual": float(ev.get("actual_value") or ev.get("actual") or 0.0),
                "forecast": float(ev.get("forecast_value") or ev.get("forecast") or 0.0),
                "previous": float(ev.get("prev_value") or ev.get("previous") or 0.0),
                "impact": str(ev.get("importance") or ev.get("impact") or "high"),
            })

        df = pl.DataFrame(normalized).sort("timestamp")
        df.write_parquet(self.cache_path)
        return df

    def load_cached_calendar(self) -> pl.DataFrame:
        """Loads cached calendar events from parquet, auto-seeding benchmark if missing."""
        if self.cache_path.exists():
            try:
                df = pl.read_parquet(self.cache_path).sort("timestamp")
                if not df.is_empty():
                    return df
            except Exception:
                pass
        from .historical_calendar_seed import generate_benchmark_g8_calendar
        return generate_benchmark_g8_calendar()

