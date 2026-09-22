from pathlib import Path
from typing import Optional
import polars as pl
from .bridge_client import BridgeClient
from ..config import settings

COMMON_CANDLES_DIR = Path(r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\fyodor_candles")

class CandleLoader:
    """Manages ingestion, local parquet caching, and loading of OHLC candles."""

    def __init__(self, bridge: Optional[BridgeClient] = None):
        self.bridge = bridge or BridgeClient()
        settings.ensure_directories()

    def _get_cache_path(self, symbol: str, timeframe: str) -> Path:
        clean_symbol = symbol.replace(".", "_").replace("#", "_")
        return settings.cache_dir / f"candles_{clean_symbol}_{timeframe}.parquet"

    def _get_common_csv_path(self, symbol: str, timeframe: str) -> Path:
        clean_symbol = symbol.replace(".", "_").replace("#", "_")
        return COMMON_CANDLES_DIR / f"candles_{clean_symbol}_{timeframe}.csv"

    def ingest_from_master_csv(
        self,
        symbol: str,
        timeframe: str = "H1",
        csv_path: Optional[Path] = None,
    ) -> pl.DataFrame:
        """
        Parses genuine broker MT5 candle history CSV (Terminal/Common/Files/fyodor_candles)
        and converts it to compressed Parquet storage.
        """
        source_path = csv_path or self._get_common_csv_path(symbol, timeframe)
        if not source_path.exists():
            raise FileNotFoundError(
                f"Historical MT5 candles CSV for {symbol} ({timeframe}) not found at: {source_path}. "
                "Under the Data Integrity Covenant, synthetic candle generation is strictly forbidden."
            )

        df = pl.read_csv(
            source_path,
            schema_overrides={
                "time": pl.Int64,
                "open": pl.Float64,
                "high": pl.Float64,
                "low": pl.Float64,
                "close": pl.Float64,
                "tick_volume": pl.Int64,
                "spread": pl.Int64,
                "real_volume": pl.Int64,
            },
        ).unique(subset=["time"]).sort("time")

        if df.is_empty():
            raise ValueError(f"No candle rows could be parsed from {source_path}")

        cache_path = self._get_cache_path(symbol, timeframe)
        df.write_parquet(cache_path)
        return df

    async def sync_candles(
        self,
        symbol: str,
        timeframe: str = "H1",
        count: int = 5000,
    ) -> pl.DataFrame:
        """Fetches candles from bridge and updates local parquet cache."""
        data = await self.bridge.get_ohlc(symbol=symbol, timeframe=timeframe, count=count)
        bars = data.get("bars", [])
        if not bars:
            cached = self.load_cached_candles(symbol, timeframe)
            if cached is not None and not cached.is_empty():
                return cached
            return pl.DataFrame()

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

    def load_cached_candles(self, symbol: str, timeframe: str = "H1") -> Optional[pl.DataFrame]:
        """
        Loads cached candles from parquet if available.
        If parquet cache is missing, auto-ingests from verified MT5 common files CSV if available.
        """
        cache_path = self._get_cache_path(symbol, timeframe)
        if cache_path.exists():
            try:
                df = pl.read_parquet(cache_path).sort("time")
                if not df.is_empty():
                    return df
            except Exception:
                pass

        common_csv = self._get_common_csv_path(symbol, timeframe)
        if common_csv.exists():
            return self.ingest_from_master_csv(symbol, timeframe, common_csv)

        return None
