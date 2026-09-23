"""
Deterministic Macroeconomic Surprise & Momentum Scoring Engine
Calculates standard expectation shocks (A - F), momentum (A - P),
standardized Z-scores, and 4-quadrant macro state classifications.

Zero synthetic data. Zero random number generators. Pure deterministic arithmetic.
"""

import math
from typing import Dict, Iterable, Optional, Tuple
from .models import (
    EventFamily,
    MacroReleaseInput,
    MacroScoringResult,
    MacroState,
    is_inverted_indicator,
)


class SurpriseMomentumEngine:
    """
    Deterministic evaluation of macroeconomic data releases.

    Math:
        Raw Surprise:   Delta_S = Actual - Forecast
        Raw Momentum:   Delta_M = Actual - Previous
        Scaled Z-Score: Z = Delta_S / sigma_event
        Inversion Rule: If indicator is inverted (e.g. Unemployment), invert signs so that:
                        Positive Z/Momentum ALWAYS represents an economic tailwind for the currency.
    """

    def __init__(
        self,
        z_threshold: float = 0.25,
        default_sigma: float = 1.0,
        historical_stds: Optional[Dict[str, float]] = None,
    ):
        """
        :param z_threshold: Absolute Z-score cutoff below which a release is considered 'IN_LINE'.
        :param default_sigma: Fallback standard deviation if no historical series exists yet.
        :param historical_stds: Pre-calibrated standard deviation of surprise (A - F) per event name.
        """
        self.z_threshold = z_threshold
        self.default_sigma = default_sigma
        self.std_cache: Dict[str, float] = dict(historical_stds or {})

    def register_event_sigma(self, event_name: str, sigma: float) -> None:
        """Register the empirical historical standard deviation of surprise for an event."""
        if sigma > 1e-6 and not math.isnan(sigma):
            self.std_cache[event_name.strip()] = float(sigma)

    def calibrate_from_observations(self, historical_pairs: Iterable[Tuple[str, float, float]]) -> None:
        """
        Calibrate standard deviations from an iterable of (event_name, actual, forecast).
        Uses population/sample standard deviation of (actual - forecast).
        """
        grouped_diffs: Dict[str, list[float]] = {}
        for event_name, actual, forecast in historical_pairs:
            diff = actual - forecast
            grouped_diffs.setdefault(event_name.strip(), []).append(diff)

        for event_name, diffs in grouped_diffs.items():
            if len(diffs) >= 2:
                mean = sum(diffs) / len(diffs)
                variance = sum((x - mean) ** 2 for x in diffs) / (len(diffs) - 1)
                std_dev = math.sqrt(variance)
                if std_dev > 1e-6:
                    self.std_cache[event_name] = std_dev

    def score(self, release: MacroReleaseInput) -> MacroScoringResult:
        """
        Scores a single macroeconomic release deterministically.
        """
        act = release.actual
        fct = release.forecast
        prev = release.previous
        name = release.event_name.strip()
        inverted = is_inverted_indicator(name)

        # 1. Compute Raw Surprise (A - F)
        raw_surprise: Optional[float] = None
        if fct is not None and not math.isnan(fct):
            raw_surprise = round(act - fct, 6)

        # 2. Compute Raw Momentum (A - P)
        raw_momentum: Optional[float] = None
        if prev is not None and not math.isnan(prev):
            raw_momentum = round(act - prev, 6)

        # 3. Apply Inversion Direction
        # Normal indicator: higher actual is bullish.
        # Inverted indicator (unemployment, jobless claims): lower actual is bullish.
        effective_surprise = raw_surprise
        effective_momentum = raw_momentum
        if inverted:
            if effective_surprise is not None:
                effective_surprise = -effective_surprise
            if effective_momentum is not None:
                effective_momentum = -effective_momentum

        # 4. Standardized Volatility-Scaled Z-Score
        z_score: Optional[float] = None
        if effective_surprise is not None:
            sigma = self.std_cache.get(name, self.default_sigma)
            if sigma > 1e-6:
                z_score = round(effective_surprise / sigma, 4)
            else:
                z_score = 0.0

        # 5. Classify 4-Quadrant Macro State
        state = MacroState.IN_LINE
        description = "In-line with consensus expectations."

        if z_score is not None:
            if abs(z_score) <= self.z_threshold:
                state = MacroState.IN_LINE
                description = f"In-line: surprise (|Z|={abs(z_score):.2f}) is within normal noise band."
            elif z_score > self.z_threshold:
                # Surprise is positive (economic tailwind)
                if effective_momentum is not None and effective_momentum > 0:
                    state = MacroState.FULL_ACCELERATION
                    description = f"Full Acceleration: beat consensus (Z=+{z_score:.2f}) and expanded above previous print."
                elif effective_momentum is not None and effective_momentum < 0:
                    state = MacroState.CONFLICTED
                    description = f"Conflicted: beat consensus (Z=+{z_score:.2f}), but decelerated below previous print."
                else:
                    state = MacroState.FULL_ACCELERATION
                    description = f"Acceleration: beat consensus (Z=+{z_score:.2f}) with neutral momentum."
            else:
                # Surprise is negative (economic headwind)
                if effective_momentum is not None and effective_momentum < 0:
                    state = MacroState.FULL_DECELERATION
                    description = f"Full Deceleration: missed consensus (Z={z_score:.2f}) and contracted below previous print."
                elif effective_momentum is not None and effective_momentum > 0:
                    state = MacroState.CONFLICTED
                    description = f"Conflicted: missed consensus (Z={z_score:.2f}), but expanded above previous print."
                else:
                    state = MacroState.FULL_DECELERATION
                    description = f"Deceleration: missed consensus (Z={z_score:.2f}) with neutral momentum."

        return MacroScoringResult(
            event_name=name,
            currency=release.currency.upper(),
            family=release.family,
            actual=act,
            forecast=fct,
            previous=prev,
            raw_surprise=raw_surprise,
            raw_momentum=raw_momentum,
            effective_surprise=effective_surprise,
            effective_momentum=effective_momentum,
            z_score=z_score,
            state=state,
            is_inverted=inverted,
            description=description,
        )
