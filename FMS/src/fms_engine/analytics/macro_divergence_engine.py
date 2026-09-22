import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.event_models import EventFamily, is_inverted_indicator
from ..contracts.setup_models import SetupDirection, QuantMethod
from .surprise_engine import SurpriseEngine
from .zone_detector import ZoneDetector
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

@dataclass
class DivergenceTrigger:
    timestamp: int
    symbol: str
    direction: SetupDirection
    spread_z: float
    base_score: float
    quote_score: float
    catalyst_event: str

@dataclass
class PairMethodResult:
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

class MacroDivergenceEngine:
    """
    Method 1: [M-MSD] Macro Surprise Divergence Research Cruncher.
    Computes time-decayed rolling macroeconomic surprise momentum vectors for G8 currencies,
    evaluates pairwise divergence spreads across Major Forex Extended, and measures empirical excursions.
    """

    def __init__(
        self,
        lookback_days: int = 14,
        half_life_days: float = 5.0,
        min_divergence_z: float = 1.75,
        refractory_bars: int = 24,  # ~4 trading days between consecutive entries
    ):
        self.lookback_seconds = lookback_days * 86400
        self.decay_lambda = math.log(2.0) / (half_life_days * 86400)
        self.min_divergence_z = min_divergence_z
        self.refractory_seconds = refractory_bars * 14400

    def compute_currency_scores(
        self,
        calendar_df: pl.DataFrame,
        surprise_engine: SurpriseEngine,
    ) -> pl.DataFrame:
        """
        Pre-computes standardized, signed, and weighted surprise shocks for all releases.
        """
        if calendar_df.is_empty():
            return pl.DataFrame()

        rows: List[Dict] = []
        for row in calendar_df.iter_rows(named=True):
            event_name = row["event_name"]
            actual = float(row["actual"])
            forecast = float(row["forecast"])
            previous = float(row["previous"])
            currency = str(row["currency"]).upper()
            impact = str(row.get("impact", "high")).lower()
            ts = int(row["timestamp"])

            # Compute standardized Z-score
            surprise, _, z_score, _ = surprise_engine.evaluate_release(
                actual=actual,
                forecast=forecast,
                previous=previous,
                event_name=event_name,
            )

            # Invert sign if indicator is inverse (e.g. unemployment rate, jobless claims)
            if is_inverted_indicator(event_name):
                z_score = -z_score

            # Weight by impact
            weight = 1.0 if impact == "high" else 0.5
            weighted_z = z_score * weight

            rows.append({
                "timestamp": ts,
                "currency": currency,
                "event_name": event_name,
                "weighted_z": weighted_z,
            })

        return pl.DataFrame(rows).sort("timestamp")

    def find_divergence_triggers(
        self,
        symbol: str,
        events_df: pl.DataFrame,
    ) -> List[DivergenceTrigger]:
        """
        Identifies all historical moments where divergence spread |S_base - S_quote| >= threshold.
        """
        if symbol not in PAIR_MAPPINGS or events_df.is_empty():
            return []

        base_curr, quote_curr = PAIR_MAPPINGS[symbol]
        pair_events = events_df.filter(
            pl.col("currency").is_in([base_curr, quote_curr])
        ).sort("timestamp")

        if pair_events.is_empty():
            return []

        triggers: List[DivergenceTrigger] = []
        last_buy_ts = -10_000_000_000
        last_sell_ts = -10_000_000_000

        all_rows = pair_events.iter_rows(named=True)

        for current_row in all_rows:
            t = current_row["timestamp"]

            # Filter events within rolling lookback window: t - lookback <= t_i <= t
            window_events = pair_events.filter(
                (pl.col("timestamp") <= t) &
                (pl.col("timestamp") >= t - self.lookback_seconds)
            )

            # Compute decayed sum for Base Currency
            base_rows = window_events.filter(pl.col("currency") == base_curr)
            s_base = 0.0
            for b_row in base_rows.iter_rows(named=True):
                dt = t - b_row["timestamp"]
                s_base += b_row["weighted_z"] * math.exp(-self.decay_lambda * dt)

            # Compute decayed sum for Quote Currency
            quote_rows = window_events.filter(pl.col("currency") == quote_curr)
            s_quote = 0.0
            for q_row in quote_rows.iter_rows(named=True):
                dt = t - q_row["timestamp"]
                s_quote += q_row["weighted_z"] * math.exp(-self.decay_lambda * dt)

            spread_z = s_base - s_quote

            # BUY Divergence: Base strongly beating Quote
            if spread_z >= self.min_divergence_z:
                if t - last_buy_ts >= self.refractory_seconds:
                    triggers.append(DivergenceTrigger(
                        timestamp=t,
                        symbol=symbol,
                        direction=SetupDirection.BUY,
                        spread_z=round(spread_z, 2),
                        base_score=round(s_base, 2),
                        quote_score=round(s_quote, 2),
                        catalyst_event=current_row["event_name"],
                    ))
                    last_buy_ts = t

            # SELL Divergence: Base strongly lagging Quote
            elif spread_z <= -self.min_divergence_z:
                if t - last_sell_ts >= self.refractory_seconds:
                    triggers.append(DivergenceTrigger(
                        timestamp=t,
                        symbol=symbol,
                        direction=SetupDirection.SELL,
                        spread_z=round(spread_z, 2),
                        base_score=round(s_base, 2),
                        quote_score=round(s_quote, 2),
                        catalyst_event=current_row["event_name"],
                    ))
                    last_sell_ts = t

        return triggers

    def crunch_pair_research(
        self,
        symbol: str,
        direction: SetupDirection,
        triggers: List[DivergenceTrigger],
        candles: pl.DataFrame,
        excursion_engine: Optional[ExcursionEngine] = None,
        use_zone_confluence: bool = True,
    ) -> Optional[PairMethodResult]:
        """
        Executes empirical excursion and survival calculations for a pair and direction,
        optionally filtered by S&R zone confluence.
        """
        if symbol not in PAIR_MAPPINGS or candles.is_empty():
            return None

        base_curr, quote_curr = PAIR_MAPPINGS[symbol]
        dir_triggers = [t for t in triggers if t.direction == direction]

        # Apply Support & Resistance Zone Confluence Filter
        if use_zone_confluence:
            detector = ZoneDetector(k_window=5, atr_period=14)
            df_atr = detector.calculate_atr(candles)
            times = df_atr["time"].to_numpy()
            opens = df_atr["open"].to_numpy()
            atrs = df_atr["atr"].to_numpy()
            is_long = direction == SetupDirection.BUY

            filtered: List[DivergenceTrigger] = []
            for t in dir_triggers:
                idx = int(np.searchsorted(times, t.timestamp))
                if idx < 30 or idx >= len(times) - 24:
                    continue
                entry = opens[idx]
                atr = atrs[idx]
                sub_df = df_atr.slice(max(0, idx - 150), min(150, idx))
                zones = detector.detect_zones(sub_df, max_zones=6)

                supp_zones = [z for z in zones if z.zone_type == "support"]
                res_zones = [z for z in zones if z.zone_type == "resistance"]

                if is_long:
                    near_supp = any(abs(entry - z.mid_price) <= 2.0 * atr for z in supp_zones) if supp_zones else True
                    not_at_res = all((z.bottom_price - entry) > 0.3 * atr or (entry > z.top_price) for z in res_zones) if res_zones else True
                    if near_supp and not_at_res:
                        filtered.append(t)
                else:
                    near_res = any(abs(entry - z.mid_price) <= 2.0 * atr for z in res_zones) if res_zones else True
                    not_at_supp = all((entry - z.top_price) > 0.3 * atr or (entry < z.bottom_price) for z in supp_zones) if supp_zones else True
                    if near_res and not_at_supp:
                        filtered.append(t)

            dir_triggers = filtered

        timestamps = [t.timestamp for t in dir_triggers]
        if len(timestamps) < 3:
            return None

        engine = excursion_engine or ExcursionEngine(max_bars=24)
        excursion_res = engine.evaluate_setup_excursions(symbol, direction, timestamps, candles)

        if excursion_res is None:
            return None

        return PairMethodResult(
            symbol=symbol,
            base_currency=base_curr,
            quote_currency=quote_curr,
            direction=direction,
            trigger_count=excursion_res.sample_count,
            win_count=excursion_res.win_count,
            loss_count=excursion_res.loss_count,
            respect_rate=excursion_res.respect_rate,
            median_mfe_pips=excursion_res.median_mfe_pips,
            mae_85_pips=excursion_res.mae_85_pips,
            recommended_sl_pips=excursion_res.recommended_sl_pips,
            recommended_tp_pips=excursion_res.recommended_tp_pips,
            reward_risk_ratio=excursion_res.reward_risk_ratio,
            avg_holding_bars=excursion_res.avg_holding_bars,
            net_realized_r=excursion_res.net_realized_r,
            expected_r_per_trade=excursion_res.expected_r_per_trade,
            valid_edge=excursion_res.valid_edge,
            k_sl=excursion_res.k_sl,
        )
