from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import polars as pl

@dataclass
class LiquidityZone:
    zone_type: str  # "resistance" or "support"
    top_price: float
    bottom_price: float
    mid_price: float
    timestamp: int
    strength: int = 1

class ZoneDetector:
    """Detects 2D Support & Resistance liquidity zones from OHLC candles."""

    def __init__(self, k_window: int = 5, atr_period: int = 14):
        self.k_window = k_window
        self.atr_period = atr_period

    def calculate_atr(self, df: pl.DataFrame) -> pl.DataFrame:
        """Appends true range and ATR columns to candle DataFrame."""
        if df.is_empty() or len(df) < self.atr_period:
            return df.with_columns(pl.lit(0.0010).alias("atr"))

        highs = df["high"].to_numpy()
        lows = df["low"].to_numpy()
        closes = df["close"].to_numpy()

        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        tr = np.insert(tr, 0, highs[0] - lows[0])

        # Simple moving average for ATR
        atr = np.zeros_like(tr)
        if len(tr) >= self.atr_period:
            atr[:self.atr_period] = np.mean(tr[:self.atr_period])
            for i in range(self.atr_period, len(tr)):
                atr[i] = (atr[i - 1] * (self.atr_period - 1) + tr[i]) / self.atr_period

        return df.with_columns(pl.Series("atr", atr))

    def detect_zones(self, df: pl.DataFrame, max_zones: int = 6) -> List[LiquidityZone]:
        """Identifies prominent swing high/low zones with ATR wick buffer."""
        if len(df) < (self.k_window * 2 + 1):
            return []

        df_with_atr = self.calculate_atr(df)
        highs = df_with_atr["high"].to_numpy()
        lows = df_with_atr["low"].to_numpy()
        closes = df_with_atr["close"].to_numpy()
        atrs = df_with_atr["atr"].to_numpy()
        times = df_with_atr["time"].to_numpy()

        zones: List[LiquidityZone] = []
        n = len(df)
        k = self.k_window

        # Scan for swing pivot highs (Resistance) and swing pivot lows (Support)
        for i in range(k, n - k):
            current_high = highs[i]
            current_low = lows[i]
            current_atr = atrs[i] if atrs[i] > 1e-5 else 0.0010
            wick_spread = 0.25 * current_atr

            # Pivot High Check
            is_pivot_high = np.all(current_high >= highs[i - k : i]) and np.all(current_high >= highs[i + 1 : i + k + 1])
            if is_pivot_high:
                bottom = max(float(closes[i]), float(current_high - wick_spread))
                zones.append(LiquidityZone(
                    zone_type="resistance",
                    top_price=float(current_high),
                    bottom_price=float(bottom),
                    mid_price=(float(current_high) + float(bottom)) / 2,
                    timestamp=int(times[i]),
                ))

            # Pivot Low Check
            is_pivot_low = np.all(current_low <= lows[i - k : i]) and np.all(current_low <= lows[i + 1 : i + k + 1])
            if is_pivot_low:
                top = min(float(closes[i]), float(current_low + wick_spread))
                zones.append(LiquidityZone(
                    zone_type="support",
                    top_price=float(top),
                    bottom_price=float(current_low),
                    mid_price=(float(top) + float(current_low)) / 2,
                    timestamp=int(times[i]),
                ))

        # Sort by most recent and return top N zones
        zones.sort(key=lambda z: z.timestamp, reverse=True)
        return zones[:max_zones]
