from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.setup_models import SetupDirection, QuantMethod
from .zone_detector import LiquidityZone, ZoneDetector
from .excursion_engine import ExcursionEngine, ExcursionResult, get_pip_scale

COMMODITY_PRODUCERS = {"AUD", "CAD", "NZD"}
NET_IMPORTERS = {"JPY", "EUR"}

PAIR_MAPPINGS: Dict[str, Tuple[str, str]] = {
    "AUDJPY": ("AUD", "JPY"),
    "EURCAD": ("EUR", "CAD"),
    "AUDUSD": ("AUD", "USD"),
    "NZDUSD": ("NZD", "USD"),
    "USDCAD": ("USD", "CAD"),
    "EURJPY": ("EUR", "JPY"),
    "GBPJPY": ("GBP", "JPY"),
    "EURGBP": ("EUR", "GBP"),
    "EURUSD": ("EUR", "USD"),
    "GBPUSD": ("GBP", "USD"),
    "USDJPY": ("USD", "JPY"),
    "USDCHF": ("USD", "CHF"),
}

@dataclass
class TermsOfTradeTrigger:
    timestamp: int
    symbol: str
    direction: SetupDirection
    tot_pulse: float
    relative_strength: float
    catalyst_event: str

@dataclass
class TermsOfTradeResult:
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

class TermsOfTradeEngine:
    """
    Method 3: [M-TOT] Terms-of-Trade Commodity Pulse.
    Measures the rolling terms-of-trade relative strength vector between commodity exporters
    (AUD, CAD, NZD) and structural net resource importers (JPY, EUR) to capture multi-week trend drift.
    """

    def __init__(
        self,
        fast_window: int = 18,        # ~3 trading days
        slow_window: int = 54,        # ~9 trading days
        min_pulse_threshold: float = 1.00,  # ATR standard deviations
        refractory_bars: int = 18,
    ):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.min_pulse = min_pulse_threshold
        self.refractory_seconds = refractory_bars * 14400

    def find_tot_triggers(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        zone_detector: Optional[ZoneDetector] = None,
    ) -> List[TermsOfTradeTrigger]:
        """
        Scans H4 bars for terms-of-trade momentum decoupling and structural zone confluence.
        """
        if symbol not in PAIR_MAPPINGS or len(candles_df) < (self.slow_window + 20):
            return []

        base_curr, quote_curr = PAIR_MAPPINGS[symbol]
        
        # Determine natural trade bias:
        # If Base is commodity exporter and Quote is net importer (e.g. AUDJPY), bias is BUY
        # If Base is net importer and Quote is commodity exporter (e.g. EURCAD), bias is SELL
        is_exporter_base = base_curr in COMMODITY_PRODUCERS
        is_importer_quote = quote_curr in NET_IMPORTERS
        is_importer_base = base_curr in NET_IMPORTERS
        is_exporter_quote = quote_curr in COMMODITY_PRODUCERS

        detector = zone_detector or ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        zones = detector.detect_zones(df_calc)

        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()
        times = df_calc["time"].to_numpy()
        n = len(closes)

        # Vectorized moving averages
        fast_sma = np.convolve(closes, np.ones(self.fast_window)/self.fast_window, mode="valid")
        slow_sma = np.convolve(closes, np.ones(self.slow_window)/self.slow_window, mode="valid")
        offset = self.slow_window - 1
        fast_aligned = fast_sma[offset - (self.fast_window - 1):]

        triggers: List[TermsOfTradeTrigger] = []
        last_trigger_ts = 0

        for i in range(len(slow_sma)):
            idx = offset + i
            if idx >= n - 24:
                break

            ts = int(times[idx])
            if (ts - last_trigger_ts) < self.refractory_seconds:
                continue

            current_close = closes[idx]
            current_atr = atrs[idx] if atrs[idx] > 1e-5 else 0.0010
            
            # Pulse: (Fast SMA - Slow SMA) normalized by ATR
            pulse = (fast_aligned[i] - slow_sma[i]) / current_atr
            rel_strength = (current_close - slow_sma[i]) / current_atr

            # Commodity Exporter Bullish Drift (e.g. AUDJPY, NZDJPY BUY)
            if pulse >= self.min_pulse and (is_exporter_base or is_importer_quote):
                direction = SetupDirection.BUY
                confluent, _ = detector.check_confluence(current_close, direction, zones, current_atr)
                if confluent:
                    triggers.append(TermsOfTradeTrigger(
                        timestamp=ts,
                        symbol=symbol,
                        direction=direction,
                        tot_pulse=round(float(pulse), 2),
                        relative_strength=round(float(rel_strength), 2),
                        catalyst_event=f"Commodity ToT Pulse (+{pulse:.2f} ATR)",
                    ))
                    last_trigger_ts = ts

            # Commodity Exporter Bearish Drift on Quote (e.g. EURCAD SELL, USDCAD SELL)
            elif pulse <= -self.min_pulse and (is_exporter_quote or is_importer_base):
                direction = SetupDirection.SELL
                confluent, _ = detector.check_confluence(current_close, direction, zones, current_atr)
                if confluent:
                    triggers.append(TermsOfTradeTrigger(
                        timestamp=ts,
                        symbol=symbol,
                        direction=direction,
                        tot_pulse=round(float(pulse), 2),
                        relative_strength=round(float(rel_strength), 2),
                        catalyst_event=f"Commodity ToT Pulse ({pulse:.2f} ATR)",
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
        reward_risk_ratio: float = 1.25,
    ) -> Optional[TermsOfTradeResult]:
        """Runs decadal backtest for Method 3 Terms of Trade setups."""
        all_triggers = self.find_tot_triggers(symbol, candles_df, zone_detector)
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

        return TermsOfTradeResult(
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
