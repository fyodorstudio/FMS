from enum import Enum
from typing import Optional, Set
from pydantic import BaseModel, Field

class MacroState(str, Enum):
    FULL_ACCELERATION = "full_acceleration"  # Strong Beat (A > F and A > P)
    FULL_DECELERATION = "full_deceleration"  # Strong Miss (A < F and A < P)
    CONFLICTED = "conflicted"                # Mixed (A > F but A < P or vice versa)
    IN_LINE = "in_line"                      # In-line (|Z| < epsilon)

class EventFamily(str, Enum):
    MONETARY_POLICY = "monetary_policy"  # Interest rates, statements, minutes
    INFLATION = "inflation"              # CPI, PPI, PCE
    LABOR = "labor"                      # NFP, Unemployment, Jobless Claims
    GROWTH = "growth"                    # GDP, Retail Sales, Industrial Production
    SENTIMENT = "sentiment"              # PMI, Consumer Confidence

INVERTED_EVENTS: Set[str] = {
    "unemployment rate",
    "jobless claims",
    "initial claims",
    "continuing claims",
    "claimant count",
}

def is_inverted_indicator(event_name: str) -> bool:
    """Returns True if higher numbers indicate economic deterioration (e.g. unemployment)."""
    lower = event_name.lower()
    return any(inv in lower for inv in INVERTED_EVENTS)

class MacroReleaseDTO(BaseModel):
    event_id: str
    event_name: str
    currency: str
    family: EventFamily
    timestamp: int  # Unix timestamp in seconds
    actual: float
    forecast: Optional[float] = None
    previous: Optional[float] = None
    surprise: Optional[float] = None
    momentum: Optional[float] = None
    z_score: Optional[float] = None
    state: MacroState = MacroState.IN_LINE
    impact: str = "high"
