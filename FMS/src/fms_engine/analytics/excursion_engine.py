from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
import polars as pl
from ..contracts.event_models import MacroReleaseDTO, MacroState
from ..contracts.setup_models import SetupDirection
from ..config import settings

def get_pip_scale(symbol: str) -> float:
    """Returns the price delta corresponding to 1 pip."""
    sym = symbol.upper()
    if "JPY" in sym:
        return 0.01
    if "XAU" in sym or "GOLD" in sym:
        return 0.10
    if "BTC" in sym or "CRYPTO" in sym:
        return 1.00
    return 0.0001

@dataclass
class ExcursionResult:
    sample_count: int
    respect_rate: float
    median_mfe_pips: float
    mae_85_pips: float
    recommended_sl_pips: float
    recommended_tp_pips: float
    reward_risk_ratio: float
    valid_edge: bool

class ExcursionEngine:
    """Vectorized calculation of Maximum Adverse & Favorable Excursions (MAE/MFE)."""

    def __init__(self, max_bars: int = 60):
        self.max_bars = max_bars

    def evaluate_setup_excursions(
        self,
        symbol: str,
        direction: SetupDirection,
        event_timestamps: List[int],
        candles: pl.DataFrame,
    ) -> Optional[ExcursionResult]:
        """Calculates statistical MAE, MFE, and optimal SL/TP pips across historical event releases."""
        if candles.is_empty() or len(candles) < 30 or not event_timestamps:
            return None

        pip_scale = get_pip_scale(symbol)
        times = candles["time"].to_numpy()
        opens = candles["open"].to_numpy()
        highs = candles["high"].to_numpy()
        lows = candles["low"].to_numpy()
        n_bars = len(times)

        mfes: List[float] = []
        maes: List[float] = []
        is_long = direction == SetupDirection.BUY

        for ts in event_timestamps:
            # Find the candle index closest to or immediately following the release
            idx = np.searchsorted(times, ts)
            if idx >= n_bars - 5:  # Not enough subsequent candles
                continue

            entry_price = float(opens[idx])
            horizon_end = min(idx + self.max_bars, n_bars)

            future_highs = highs[idx:horizon_end]
            future_lows = lows[idx:horizon_end]

            if is_long:
                max_high = float(np.max(future_highs))
                min_low = float(np.min(future_lows))
                mfe_pips = max(0.0, (max_high - entry_price) / pip_scale)
                mae_pips = max(0.0, (entry_price - min_low) / pip_scale)
            else:
                max_high = float(np.max(future_highs))
                min_low = float(np.min(future_lows))
                mfe_pips = max(0.0, (entry_price - min_low) / pip_scale)
                mae_pips = max(0.0, (max_high - entry_price) / pip_scale)

            mfes.append(mfe_pips)
            maes.append(mae_pips)

        if len(mfes) < 3:
            return None

        mfe_arr = np.array(mfes)
        mae_arr = np.array(maes)

        median_mfe = float(np.median(mfe_arr))
        mae_85 = float(np.percentile(mae_arr, settings.mae_percentile * 100))

        # Recommended levels with buffer
        recommended_tp = round(max(median_mfe, 15.0), 1)
        recommended_sl = round(max(mae_85 * (1 + settings.sl_atr_buffer), 10.0), 1)
        rr_ratio = round(recommended_tp / recommended_sl, 2) if recommended_sl > 0 else 1.0

        # Calculate Respect Rate: percentage of events that reached TP before reaching SL
        winning_runs = 0
        for m, a in zip(mfes, maes):
            if m >= recommended_tp and a < recommended_sl:
                winning_runs += 1

        respect_rate = round(winning_runs / len(mfes), 2)
        valid_edge = respect_rate >= settings.min_respect_rate and rr_ratio >= settings.min_reward_risk_ratio

        return ExcursionResult(
            sample_count=len(mfes),
            respect_rate=respect_rate,
            median_mfe_pips=median_mfe,
            mae_85_pips=mae_85,
            recommended_sl_pips=recommended_sl,
            recommended_tp_pips=recommended_tp,
            reward_risk_ratio=rr_ratio,
            valid_edge=valid_edge,
        )
