"""
FMS Macro Event Data Models & Contracts
Part of the Quantitative Event-Driven Engine.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Set


class MacroState(str, Enum):
    FULL_ACCELERATION = "full_acceleration"  # Strong Beat: A > F and A > P
    FULL_DECELERATION = "full_deceleration"  # Strong Miss: A < F and A < P
    CONFLICTED = "conflicted"                # Divergent: A > F but A < P (or vice versa)
    IN_LINE = "in_line"                      # In-line: |Z| <= epsilon threshold


class EventFamily(str, Enum):
    MONETARY_POLICY = "monetary_policy"  # Interest rates, statements, meeting minutes
    INFLATION = "inflation"              # CPI, Core CPI, PPI, PCE Price Index
    LABOR = "labor"                      # NFP, Unemployment Rate, Jobless Claims
    GROWTH = "growth"                    # GDP, Retail Sales, Industrial Production
    SENTIMENT = "sentiment"              # ISM PMI, S&P Global PMI, Consumer Confidence


# Indicators where higher numbers indicate economic deterioration
INVERTED_INDICATORS: Set[str] = {
    "unemployment rate",
    "jobless claims",
    "initial claims",
    "continuing claims",
    "claimant count",
    "underemployment rate",
}


def is_inverted_indicator(event_name: str) -> bool:
    """Returns True if a higher numeric print represents economic deterioration (e.g. unemployment)."""
    normalized = event_name.lower().strip()
    return any(inv in normalized for inv in INVERTED_INDICATORS)


@dataclass(frozen=True)
class MacroReleaseInput:
    """Raw macroeconomic release observation from authentic broker calendar."""
    event_name: str
    currency: str
    actual: float
    forecast: Optional[float]
    previous: Optional[float]
    family: EventFamily = EventFamily.GROWTH
    timestamp_seconds: int = 0


@dataclass(frozen=True)
class MacroScoringResult:
    """Deterministic score derived from Actual vs. Forecast vs. Previous."""
    event_name: str
    currency: str
    family: EventFamily
    actual: float
    forecast: Optional[float]
    previous: Optional[float]
    raw_surprise: Optional[float]      # Actual - Forecast
    raw_momentum: Optional[float]      # Actual - Previous
    effective_surprise: Optional[float] # Inverted if indicator is inverted
    effective_momentum: Optional[float] # Inverted if indicator is inverted
    z_score: Optional[float]           # Standardized volatility-scaled surprise
    state: MacroState                  # 4-quadrant state classification
    is_inverted: bool
    description: str
