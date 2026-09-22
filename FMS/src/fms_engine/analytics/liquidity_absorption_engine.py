from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.setup_models import SetupDirection, QuantMethod
from .zone_detector import LiquidityZone, ZoneDetector
from .excursion_engine import ExcursionEngine, ExcursionResult, get_pip_scale

@dataclass
class LiquidityAbsorptionTrigger:
    timestamp: int
    symbol: str
    direction: SetupDirection
    expansion_ratio: float
    wick_ratio: float
    candle_tr: float
    baseline_atr: float
    catalyst_event: str

@dataclass
class LiquidityAbsorptionResult:
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

class LiquidityAbsorptionEngine:
    """
    Method 5: [M-LAR] Liquidity Absorption & Sovereign Intervention Rejection.
    Detects sudden massive ATR volatility shocks (TR >= 2.0x ATR) coupled with extreme
    pin-bar rejection wicks rejecting higher-timeframe S&R Liquidity Zones to capture
    sovereign defense waves and trapped-breakout liquidation cascades.
    """

    def __init__(
        self,
        min_expansion_ratio: float = 1.50,  # TR >= 1.50x baseline ATR
        min_wick_ratio: float = 0.40,       # Rejection wick >= 40% of total candle range
        refractory_bars: int = 18,          # ~3 trading days between triggers
    ):
        self.min_expansion = min_expansion_ratio
        self.min_wick_ratio = min_wick_ratio
        self.refractory_seconds = refractory_bars * 14400

    def find_absorption_triggers(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        zone_detector: Optional[ZoneDetector] = None,
    ) -> List[LiquidityAbsorptionTrigger]:
        """Scans H4 bars for 2x+ ATR expansion shocks with extreme zone-rejection wicks."""
        if len(candles_df) < 30:
            return []

        detector = zone_detector or ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        zones = detector.detect_zones(df_calc)

        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()
        n = len(times)

        triggers: List[LiquidityAbsorptionTrigger] = []
        last_trigger_ts = 0

        for i in range(15, n - 24):
            ts = int(times[i])
            if (ts - last_trigger_ts) < self.refractory_seconds:
                continue

            o_i, h_i, l_i, c_i = opens[i], highs[i], lows[i], closes[i]
            candle_range = h_i - l_i
            curr_atr = atrs[i] if atrs[i] > 1e-5 else 0.0010

            if candle_range <= 0 or curr_atr <= 0:
                continue

            expansion_ratio = candle_range / curr_atr
            if expansion_ratio < self.min_expansion:
                continue

            upper_wick = h_i - max(o_i, c_i)
            lower_wick = min(o_i, c_i) - l_i

            upper_wick_ratio = upper_wick / candle_range
            lower_wick_ratio = lower_wick / candle_range

            # Bearish Absorption Rejection (Extreme Upper Wick off Resistance) -> SELL
            if upper_wick_ratio >= self.min_wick_ratio:
                direction = SetupDirection.SELL
                confluent, _ = detector.check_confluence(c_i, direction, zones, curr_atr)
                if confluent:
                    triggers.append(LiquidityAbsorptionTrigger(
                        timestamp=ts,
                        symbol=symbol,
                        direction=direction,
                        expansion_ratio=round(float(expansion_ratio), 2),
                        wick_ratio=round(float(upper_wick_ratio), 2),
                        candle_tr=round(float(candle_range), 5),
                        baseline_atr=round(float(curr_atr), 5),
                        catalyst_event=f"Absorption Shock ({expansion_ratio:.1f}x ATR, {upper_wick_ratio*100:.0f}% Wick)",
                    ))
                    last_trigger_ts = ts

            # Bullish Absorption Rejection (Extreme Lower Wick off Support) -> BUY
            elif lower_wick_ratio >= self.min_wick_ratio:
                direction = SetupDirection.BUY
                confluent, _ = detector.check_confluence(c_i, direction, zones, curr_atr)
                if confluent:
                    triggers.append(LiquidityAbsorptionTrigger(
                        timestamp=ts,
                        symbol=symbol,
                        direction=direction,
                        expansion_ratio=round(float(expansion_ratio), 2),
                        wick_ratio=round(float(lower_wick_ratio), 2),
                        candle_tr=round(float(candle_range), 5),
                        baseline_atr=round(float(curr_atr), 5),
                        catalyst_event=f"Absorption Shock ({expansion_ratio:.1f}x ATR, {lower_wick_ratio*100:.0f}% Wick)",
                    ))
                    last_trigger_ts = ts

        return triggers

    def backtest_pair_direction(
        self,
        symbol: str,
        direction: SetupDirection,
        candles_df: pl.DataFrame,
        excursion_engine: ExcursionEngine,
        zone_detector: Optional[ZoneDetector] = None,
        k_sl: float = 2.0,
        reward_risk_ratio: float = 1.00,
    ) -> Optional[LiquidityAbsorptionResult]:
        """Runs decadal backtest for Method 5 Liquidity Absorption setups."""
        all_triggers = self.find_absorption_triggers(symbol, candles_df, zone_detector)
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

        base_curr = symbol[:3]
        quote_curr = symbol[3:]

        return LiquidityAbsorptionResult(
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
