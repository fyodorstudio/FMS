import math
from typing import Dict, Optional, Tuple
import polars as pl
from ..contracts.event_models import MacroReleaseDTO, MacroState, EventFamily

class SurpriseEngine:
    """Computes standardized Z-score surprises, momentum, and 4-state classifications."""

    def __init__(self, historical_events: Optional[pl.DataFrame] = None):
        self.std_cache: Dict[str, float] = {}
        if historical_events is not None and not historical_events.is_empty():
            self.calibrate_standard_deviations(historical_events)

    def calibrate_standard_deviations(self, df: pl.DataFrame) -> None:
        """Calibrates surprise standard deviation per event name and family."""
        if "actual" not in df.columns or "forecast" not in df.columns:
            return

        df_calc = df.with_columns(
            (pl.col("actual") - pl.col("forecast")).alias("diff")
        ).filter(pl.col("diff").is_not_null() & (pl.col("diff") != 0.0))

        if df_calc.is_empty():
            return

        # Per-event name std
        grouped_name = df_calc.group_by("event_name").agg(
            pl.col("diff").std().alias("std_diff"),
            pl.len().alias("count"),
        )
        for row in grouped_name.iter_rows(named=True):
            if row["std_diff"] and not math.isnan(row["std_diff"]) and row["std_diff"] > 1e-6:
                self.std_cache[row["event_name"]] = float(row["std_diff"])

        # Per-family std fallback
        grouped_family = df_calc.group_by("family").agg(
            pl.col("diff").std().alias("std_diff"),
        )
        for row in grouped_family.iter_rows(named=True):
            if row["std_diff"] and not math.isnan(row["std_diff"]) and row["std_diff"] > 1e-6:
                self.std_cache[f"family_{row['family']}"] = float(row["std_diff"])

    def evaluate_release(
        self,
        actual: float,
        forecast: float,
        previous: float,
        event_name: str,
        family: EventFamily = EventFamily.GROWTH,
    ) -> Tuple[float, float, float, MacroState]:
        """
        Calculates (surprise, momentum, z_score, state) for a release.
        """
        surprise = actual - forecast
        momentum = actual - previous

        # Determine standard deviation for normalization
        sigma = self.std_cache.get(event_name) or self.std_cache.get(f"family_{family.value}") or 1.0
        z_score = surprise / sigma if sigma > 1e-6 else 0.0

        # Classify Macro State
        threshold = 0.25
        if abs(z_score) <= threshold:
            state = MacroState.IN_LINE
        elif z_score > threshold and momentum > 0:
            state = MacroState.FULL_ACCELERATION
        elif z_score < -threshold and momentum < 0:
            state = MacroState.FULL_DECELERATION
        else:
            state = MacroState.CONFLICTED

        return surprise, momentum, z_score, state
