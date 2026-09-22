import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.event_models import EventFamily
from ..contracts.setup_models import SetupDirection, QuantMethod
from .zone_detector import LiquidityZone, ZoneDetector
from .excursion_engine import ExcursionEngine, ExcursionResult, get_pip_scale

PAIR_MAPPINGS: Dict[str, Tuple[str, str]] = {
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDJPY": ("USD", "JPY"),
    "AUDUSD": ("AUD", "USD"),
    "USDCAD": ("USD", "CAD"),
    "USDCHF": ("USD", "CHF"),
    "NZDUSD": ("NZD", "USD"),
    "EURJPY": ("EUR", "JPY"),
    "GBPJPY": ("GBP", "JPY"),
    "EURGBP": ("EUR", "GBP"),
    "AUDJPY": ("AUD", "JPY"),
    "EURCAD": ("EUR", "CAD"),
}

# Baseline anchor inflation rates when historical country releases are pending
BASELINE_CPI: Dict[str, float] = {
    "USD": 2.50,
    "EUR": 2.00,
    "GBP": 2.50,
    "JPY": 1.50,
    "AUD": 2.80,
    "CAD": 2.50,
    "CHF": 1.20,
    "NZD": 2.80,
}

@dataclass
class PolicyTrigger:
    timestamp: int
    symbol: str
    direction: SetupDirection
    nominal_spread: float
    real_spread: float
    spread_momentum: float
    base_policy_rate: float
    quote_policy_rate: float
    catalyst_event: str

@dataclass
class PolicyMethodResult:
    symbol: str
    base_currency: str
    quote_currency: str
    direction: SetupDirection
    trigger_count: int
    win_count: int
    loss_count: int
    respect_rate: float
    median_mfe_pips: float
    mae_85_pips: float
    recommended_sl_pips: float
    recommended_tp_pips: float
    reward_risk_ratio: float
    avg_holding_bars: float
    net_realized_r: float
    expected_r_per_trade: float
    valid_edge: bool
    k_sl: float = 2.0

class PolicySpreadEngine:
    """
    Method 2: [M-PYS] Policy & Real Yield Spread Momentum.
    Measures the rolling sovereign interest rate differential and inflation-adjusted real yield
    spreads across G8 currency pairs to harvest multi-week macroeconomic trends.
    """

    def __init__(
        self,
        min_real_spread_bps: float = 100.0,   # At least 1.00% (100 bps) real yield advantage
        momentum_lookback_days: int = 90,     # ~1 quarter policy momentum window
        refractory_bars: int = 12,            # ~2 trading days between consecutive entries
    ):
        self.min_real_spread = min_real_spread_bps / 100.0
        self.momentum_seconds = momentum_lookback_days * 86400
        self.refractory_seconds = refractory_bars * 14400

    def extract_macro_state_timeline(
        self,
        calendar_df: pl.DataFrame
    ) -> Dict[str, List[Tuple[int, float, float]]]:
        """
        Builds a chronological timeline of (timestamp, policy_rate, cpi_yoy) for each G8 currency.
        """
        timeline: Dict[str, List[Tuple[int, float, float]]] = {
            curr: [] for curr in BASELINE_CPI.keys()
        }

        # Filter calendar to policy and inflation events with valid actual values
        relevant_df = calendar_df.filter(
            pl.col("family").is_in(["monetary_policy", "inflation"]) &
            pl.col("actual").is_not_null()
        ).sort("timestamp")

        current_rates: Dict[str, float] = {curr: 1.0 for curr in BASELINE_CPI.keys()}
        current_cpis: Dict[str, float] = BASELINE_CPI.copy()

        for row in relevant_df.iter_rows(named=True):
            curr = row["currency"]
            ts = row["timestamp"]
            actual = row["actual"]
            family = row["family"]

            if actual is None:
                continue
            try:
                val = float(actual)
            except (ValueError, TypeError):
                continue

            if curr in current_rates:
                if family == "monetary_policy":
                    current_rates[curr] = val
                elif family == "inflation":
                    current_cpis[curr] = val

                timeline[curr].append((ts, current_rates[curr], current_cpis[curr]))

        return timeline

    def get_state_at(
        self,
        timeline: List[Tuple[int, float, float]],
        target_ts: int,
        curr: str
    ) -> Tuple[float, float]:
        """Binary search to get the active policy rate and CPI at target_ts."""
        if not timeline:
            return 1.5, BASELINE_CPI.get(curr, 2.0)
        
        low, high = 0, len(timeline) - 1
        best_idx = -1
        while low <= high:
            mid = (low + high) // 2
            if timeline[mid][0] <= target_ts:
                best_idx = mid
                low = mid + 1
            else:
                high = mid - 1

        if best_idx >= 0:
            return timeline[best_idx][1], timeline[best_idx][2]
        return timeline[0][1], timeline[0][2]

    def find_policy_triggers(
        self,
        symbol: str,
        calendar_df: pl.DataFrame,
        candles_df: pl.DataFrame,
        zone_detector: Optional[ZoneDetector] = None,
    ) -> List[PolicyTrigger]:
        """
        Scans macroeconomic releases for high-conviction Policy and Real Yield Spread divergence triggers.
        Anchored to actual Central Bank rate decisions and CPI releases.
        """
        if symbol not in PAIR_MAPPINGS:
            return []
        
        base_curr, quote_curr = PAIR_MAPPINGS[symbol]
        timeline = self.extract_macro_state_timeline(calendar_df)
        base_timeline = timeline[base_curr]
        quote_timeline = timeline[quote_curr]

        # Filter events belonging to base or quote
        pair_events = calendar_df.filter(
            (pl.col("currency").is_in([base_curr, quote_curr])) &
            (pl.col("family").is_in(["monetary_policy", "inflation"]))
        ).sort("timestamp")

        # Precompute zones if enabled
        zones = zone_detector.detect_zones(candles_df) if zone_detector else []

        triggers: List[PolicyTrigger] = []
        last_trigger_ts = 0

        for row in pair_events.iter_rows(named=True):
            ts = row["timestamp"]
            event_name = row["event_name"]

            if (ts - last_trigger_ts) < self.refractory_seconds:
                continue

            # Query candle at timestamp
            matching = candles_df.filter(pl.col("time") >= ts).head(1)
            if matching.is_empty():
                continue
            candle_price = matching["close"][0]

            # Get current policy and CPI state
            i_base, cpi_base = self.get_state_at(base_timeline, ts, base_curr)
            i_quote, cpi_quote = self.get_state_at(quote_timeline, ts, quote_curr)

            # Get past states (90 days ago for momentum)
            past_ts = ts - self.momentum_seconds
            i_base_past, _ = self.get_state_at(base_timeline, past_ts, base_curr)
            i_quote_past, _ = self.get_state_at(quote_timeline, past_ts, quote_curr)

            # Real yields: r = i - cpi
            if any(v is None for v in (i_base, cpi_base, i_quote, cpi_quote, i_base_past, i_quote_past)):
                continue

            r_base = float(i_base) - float(cpi_base)
            r_quote = float(i_quote) - float(cpi_quote)
            real_spread = r_base - r_quote

            # Nominal spread & momentum
            nominal_spread = i_base - i_quote
            nominal_spread_past = i_base_past - i_quote_past
            spread_momentum = nominal_spread - nominal_spread_past

            # Evaluate BUY condition:
            # Positive real yield spread (>= +1.00%)
            if real_spread >= self.min_real_spread:
                direction = SetupDirection.BUY
                if zone_detector:
                    is_confluent, _ = zone_detector.check_confluence(candle_price, direction, zones)
                    if not is_confluent:
                        continue
                
                triggers.append(PolicyTrigger(
                    timestamp=ts,
                    symbol=symbol,
                    direction=direction,
                    nominal_spread=round(nominal_spread, 2),
                    real_spread=round(real_spread, 2),
                    spread_momentum=round(spread_momentum, 2),
                    base_policy_rate=i_base,
                    quote_policy_rate=i_quote,
                    catalyst_event=f"{event_name} (Real Spread: +{real_spread:.2f}%)",
                ))
                last_trigger_ts = ts

            # Evaluate SELL condition:
            # Negative real yield spread (<= -1.00%)
            elif real_spread <= -self.min_real_spread:
                direction = SetupDirection.SELL
                if zone_detector:
                    is_confluent, _ = zone_detector.check_confluence(candle_price, direction, zones)
                    if not is_confluent:
                        continue
                
                triggers.append(PolicyTrigger(
                    timestamp=ts,
                    symbol=symbol,
                    direction=direction,
                    nominal_spread=round(nominal_spread, 2),
                    real_spread=round(real_spread, 2),
                    spread_momentum=round(spread_momentum, 2),
                    base_policy_rate=i_base,
                    quote_policy_rate=i_quote,
                    catalyst_event=f"{event_name} (Real Spread: {real_spread:.2f}%)",
                ))
                last_trigger_ts = ts

        return triggers

    def backtest_pair_direction(
        self,
        symbol: str,
        direction: SetupDirection,
        calendar_df: pl.DataFrame,
        candles_df: pl.DataFrame,
        excursion_engine: ExcursionEngine,
        zone_detector: Optional[ZoneDetector] = None,
        k_sl: float = 2.0,
        reward_risk_ratio: float = 1.25,
    ) -> Optional[PolicyMethodResult]:
        """
        Runs empirical decadal backtest for a specific symbol and direction under Method 2.
        """
        all_triggers = self.find_policy_triggers(symbol, calendar_df, candles_df, zone_detector)
        dir_triggers = [t for t in all_triggers if t.direction == direction]

        if not dir_triggers or len(dir_triggers) < 5:
            return None

        timestamps = [t.timestamp for t in dir_triggers]
        excursion = excursion_engine.evaluate_setup_excursions(
            symbol=symbol,
            direction=direction,
            event_timestamps=timestamps,
            candles=candles_df,
            k_sl_fixed=k_sl,
            rr_fixed=reward_risk_ratio,
        )

        if not excursion or excursion.sample_count < 5:
            return None

        base_curr, quote_curr = PAIR_MAPPINGS.get(symbol, ("USD", "USD"))

        return PolicyMethodResult(
            symbol=symbol,
            base_currency=base_curr,
            quote_currency=quote_curr,
            direction=direction,
            trigger_count=excursion.sample_count,
            win_count=excursion.win_count,
            loss_count=excursion.loss_count,
            respect_rate=round(excursion.respect_rate, 4),
            median_mfe_pips=round(excursion.median_mfe_pips, 1),
            mae_85_pips=round(excursion.mae_85_pips, 1),
            recommended_sl_pips=round(excursion.recommended_sl_pips, 1),
            recommended_tp_pips=round(excursion.recommended_tp_pips, 1),
            reward_risk_ratio=round(excursion.reward_risk_ratio, 2),
            avg_holding_bars=round(excursion.avg_holding_bars, 1),
            net_realized_r=round(excursion.net_realized_r, 2),
            expected_r_per_trade=round(excursion.expected_r_per_trade, 3),
            valid_edge=bool(excursion.valid_edge),
            k_sl=k_sl,
        )
