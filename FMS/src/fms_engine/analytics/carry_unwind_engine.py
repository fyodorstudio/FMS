from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.setup_models import SetupDirection, QuantMethod
from .zone_detector import LiquidityZone, ZoneDetector
from .excursion_engine import ExcursionEngine, ExcursionResult, get_pip_scale

# Carry funding currencies and their primary liquid carry pairs
FUNDING_PAIRS: Dict[str, SetupDirection] = {
    "USDJPY": SetupDirection.SELL,
    "EURJPY": SetupDirection.SELL,
    "GBPJPY": SetupDirection.SELL,
    "AUDJPY": SetupDirection.SELL,
    "USDCHF": SetupDirection.SELL,
    "AUDUSD": SetupDirection.SELL,
    "NZDUSD": SetupDirection.SELL,
    "EURCAD": SetupDirection.BUY,
}

@dataclass
class CarryUnwindTrigger:
    timestamp: int
    symbol: str
    direction: SetupDirection
    volatility_z: float
    current_atr: float
    baseline_atr: float
    catalyst_event: str

@dataclass
class CarryUnwindResult:
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

class CarryUnwindEngine:
    """
    Method 4: [M-VRC] Volatility Regime & Carry Unwind.
    Detects market-wide volatility regime expansion shocks (Z_vol >= 1.50) and captures
    systemic liquidation cascades where carry trades are violently liquidated.
    """

    def __init__(
        self,
        lookback_baseline: int = 60,   # ~10 trading days baseline
        min_vol_z: float = 1.50,       # Standard deviations above baseline
        refractory_bars: int = 24,     # ~4 trading days between consecutive entries
    ):
        self.lookback_baseline = lookback_baseline
        self.min_vol_z = min_vol_z
        self.refractory_seconds = refractory_bars * 14400

    def find_unwind_triggers(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        zone_detector: Optional[ZoneDetector] = None,
    ) -> List[CarryUnwindTrigger]:
        """Scans for volatility regime expansion triggers on carry-sensitive pairs."""
        if len(candles_df) < (self.lookback_baseline + 30):
            return []

        detector = zone_detector or ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        zones = detector.detect_zones(df_calc)

        atrs = df_calc["atr"].to_numpy()
        times = df_calc["time"].to_numpy()
        closes = df_calc["close"].to_numpy()
        n = len(atrs)

        triggers: List[CarryUnwindTrigger] = []
        last_trigger_ts = 0

        # Compute rolling mean and std of ATR
        for i in range(self.lookback_baseline, n - 24):
            ts = int(times[i])
            if (ts - last_trigger_ts) < self.refractory_seconds:
                continue

            window_atrs = atrs[i - self.lookback_baseline : i]
            mean_atr = np.mean(window_atrs)
            std_atr = np.std(window_atrs)

            if std_atr < 1e-6:
                continue

            curr_atr = atrs[i]
            vol_z = (curr_atr - mean_atr) / std_atr

            # Volatility expansion shock indicates liquidation
            if vol_z >= self.min_vol_z:
                # Default direction for carry unwind (funding repatriation)
                direction = FUNDING_PAIRS.get(symbol, SetupDirection.SELL)

                confluent, _ = detector.check_confluence(closes[i], direction, zones, curr_atr)
                if not confluent:
                    continue

                triggers.append(CarryUnwindTrigger(
                    timestamp=ts,
                    symbol=symbol,
                    direction=direction,
                    volatility_z=round(float(vol_z), 2),
                    current_atr=round(float(curr_atr), 5),
                    baseline_atr=round(float(mean_atr), 5),
                    catalyst_event=f"Volatility Regime Shock (Z={vol_z:.2f} sigma)",
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
    ) -> Optional[CarryUnwindResult]:
        """Runs decadal backtest for Method 4 Carry Unwind setups."""
        all_triggers = self.find_unwind_triggers(symbol, candles_df, zone_detector)
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

        return CarryUnwindResult(
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
