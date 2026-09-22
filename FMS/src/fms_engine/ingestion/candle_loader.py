from pathlib import Path
from typing import Optional
import polars as pl
from .bridge_client import BridgeClient
from ..config import settings

class CandleLoader:
    """Manages ingestion, local parquet caching, and loading of OHLC candles."""

    def __init__(self, bridge: Optional[BridgeClient] = None):
        self.bridge = bridge or BridgeClient()
        settings.ensure_directories()

    def _get_cache_path(self, symbol: str, timeframe: str) -> Path:
        clean_symbol = symbol.replace(".", "_").replace("#", "_")
        return settings.cache_dir / f"candles_{clean_symbol}_{timeframe}.parquet"

    async def sync_candles(
        self,
        symbol: str,
        timeframe: str = "H4",
        count: int = 1600,
    ) -> pl.DataFrame:
        """Fetches candles from bridge and updates local parquet cache."""
        data = await self.bridge.get_ohlc(symbol=symbol, timeframe=timeframe, count=count)
        bars = data.get("bars", [])
        if not bars:
            return self.load_cached_candles(symbol, timeframe) or pl.DataFrame()

        df_new = pl.DataFrame(bars).sort("time")
        cache_path = self._get_cache_path(symbol, timeframe)

        if cache_path.exists():
            try:
                df_existing = pl.read_parquet(cache_path)
                df_combined = (
                    pl.concat([df_existing, df_new])
                    .unique(subset=["time"])
                    .sort("time")
                )
                df_combined.write_parquet(cache_path)
                return df_combined
            except Exception:
                pass

        df_new.write_parquet(cache_path)
        return df_new

    def load_cached_candles(self, symbol: str, timeframe: str = "H4") -> Optional[pl.DataFrame]:
        """Loads cached candles from parquet if available."""
        cache_path = self._get_cache_path(symbol, timeframe)
        if cache_path.exists():
            try:
                return pl.read_parquet(cache_path).sort("time")
            except Exception:
                return None
        return None

