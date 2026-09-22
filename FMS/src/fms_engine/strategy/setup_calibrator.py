import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.setup_models import RegisteredSetupDTO, SetupDirection, QuantMethod
from ..ingestion.calendar_loader import CalendarLoader
from ..ingestion.candle_loader import CandleLoader
from ..analytics.signal_evaluator import SignalEvaluator, PAIR_CURRENCIES
from ..strategy.setup_registry import SetupRegistry

CORE_SYMBOLS = [
    "EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURJPY", "GBPJPY", "EURGBP", "AUDJPY", "EURCAD", "XAUUSD"
]


class SetupCalibrator:
    """
    Discovers, verifies, and registers codified macro trading setups
    strictly from genuine MT5 broker data under the Quality Gate.
    Enforces bidirectional calibration (distinct BUY and SELL setups)
    across all 5 quantitative factor models.
    """

    def __init__(self, registry: Optional[SetupRegistry] = None):
        self.registry = registry or SetupRegistry()
        self.calendar_loader = CalendarLoader()
        self.candle_loader = CandleLoader()
        self.evaluator = SignalEvaluator(horizon_bars=24, k_sl=2.0, rr_target=1.25)

    def _register_signals_by_direction(
        self,
        sym: str,
        sigs: List[Dict[str, Any]],
        quant_method: QuantMethod,
        trigger_state: str,
        min_sample_size: int,
        min_win_rate: float,
        min_z_score: float,
        now_ts: int,
    ) -> List[RegisteredSetupDTO]:
        """
        Groups evaluated signals by (event_name, direction) to evaluate
        BUY and SELL setups independently with zero composite pooling.
        """
        registered: List[RegisteredSetupDTO] = []
        groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

        for s in sigs:
            ev_name = s.get("event_name", "Macro Catalyst")
            direction_str = s.get("direction", "long")
            groups.setdefault((ev_name, direction_str), []).append(s)

        for (ev_name, direction_str), group_sigs in groups.items():
            tot = len(group_sigs)
            if tot < min_sample_size:
                continue

            wins = sum(1 for s in group_sigs if s["result"] == "tp-reached")
            wr = wins / tot
            net_r = sum(s["result_r"] for s in group_sigs if s["result_r"] is not None)

            # Empirical Quality Gate: Win Rate >= min_win_rate AND positive cumulative Net R
            if wr >= min_win_rate and net_r > 0.0:
                mfes = [s["mfe_pips"] for s in group_sigs]
                maes = [s["mae_pips"] for s in group_sigs]
                sl_pips = [s["recommended_sl_pips"] for s in group_sigs]
                tp_pips = [s["recommended_tp_pips"] for s in group_sigs]

                setup_direction = SetupDirection.BUY if direction_str == "long" else SetupDirection.SELL
                clean_name = ev_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")[:35]
                setup_id = f"{quant_method.name}_{sym}_{setup_direction.value}_{clean_name}"

                base_ccy = PAIR_CURRENCIES.get(sym, (sym[:3], sym[3:]))[0]

                setup_dto = RegisteredSetupDTO(
                    id=setup_id,
                    quant_method=quant_method,
                    event_name=ev_name,
                    currency=base_ccy,
                    symbol=sym,
                    direction=setup_direction,
                    timeframe="H1",
                    respect_rate=round(wr, 3),
                    sample_count=tot,
                    median_mfe_pips=round(float(np.median(mfes)), 1),
                    mae_85_pips=round(float(np.percentile(maes, 85)), 1),
                    recommended_sl_pips=round(float(np.median(sl_pips)), 1),
                    recommended_tp_pips=round(float(np.median(tp_pips)), 1),
                    reward_risk_ratio=1.25,
                    trigger_state=trigger_state,
                    min_z_score=min_z_score,
                    active=True,
                    created_at=now_ts,
                )
                self.registry.save_setup(setup_dto)
                registered.append(setup_dto)

        return registered

    def run_calibration(
        self,
        symbols: Optional[List[str]] = None,
        min_sample_size: int = 15,
        min_win_rate: float = 0.48,
    ) -> List[RegisteredSetupDTO]:
        """
        Scans genuine MT5 history, evaluates empirical paths, and registers qualifying setups.
        Wipes old flawed setups and repopulates SQLite with bidirectional multi-method setups.
        """
        target_symbols = symbols or CORE_SYMBOLS
        cal_df = self.calendar_loader.load_cached_calendar()
        self.registry.clear_setups()

        registered: List[RegisteredSetupDTO] = []
        now_ts = int(time.time())

        for sym in target_symbols:
            candles_df = self.candle_loader.load_cached_candles(sym, "H1")
            if candles_df is None or len(candles_df) < 1000:
                continue

            # Method 1: Macro Surprise Divergence (M-MSD)
            if sym in PAIR_CURRENCIES and cal_df is not None and not cal_df.is_empty():
                msd_sigs = self.evaluator.generate_calendar_signals(
                    symbol=sym,
                    calendar_df=cal_df,
                    candles_df=candles_df,
                    min_abs_z=0.50,
                    max_signals=0,
                )
                registered.extend(self._register_signals_by_direction(
                    sym=sym,
                    sigs=msd_sigs,
                    quant_method=QuantMethod.MSD,
                    trigger_state="full_acceleration",
                    min_sample_size=min_sample_size,
                    min_win_rate=min_win_rate,
                    min_z_score=0.50,
                    now_ts=now_ts,
                ))

            # Method 2: Policy & Real Yield Spread Momentum (M-PYS)
            if sym in PAIR_CURRENCIES and cal_df is not None and not cal_df.is_empty():
                pys_sigs = self.evaluator.generate_pys_signals(
                    symbol=sym,
                    calendar_df=cal_df,
                    candles_df=candles_df,
                    max_signals=0,
                )
                registered.extend(self._register_signals_by_direction(
                    sym=sym,
                    sigs=pys_sigs,
                    quant_method=QuantMethod.PYS,
                    trigger_state="policy_divergence",
                    min_sample_size=min_sample_size,
                    min_win_rate=min_win_rate,
                    min_z_score=1.00,
                    now_ts=now_ts,
                ))

            # Method 3: Terms-of-Trade Commodity Pulse (M-TOT)
            tot_sigs = self.evaluator.generate_tot_signals(
                symbol=sym,
                candles_df=candles_df,
                max_signals=0,
            )
            registered.extend(self._register_signals_by_direction(
                sym=sym,
                sigs=tot_sigs,
                quant_method=QuantMethod.TOT,
                trigger_state="commodity_pulse",
                min_sample_size=min_sample_size,
                min_win_rate=min_win_rate,
                min_z_score=1.00,
                now_ts=now_ts,
            ))

            # Method 4: Volatility Regime & Carry Unwind (M-VRC)
            vrc_sigs = self.evaluator.generate_vrc_signals(
                symbol=sym,
                candles_df=candles_df,
                max_signals=0,
            )
            registered.extend(self._register_signals_by_direction(
                sym=sym,
                sigs=vrc_sigs,
                quant_method=QuantMethod.VRC,
                trigger_state="carry_liquidation",
                min_sample_size=min_sample_size,
                min_win_rate=min_win_rate,
                min_z_score=1.50,
                now_ts=now_ts,
            ))

            # Method 5: Liquidity Absorption Rejection (M-LAR)
            lar_sigs = self.evaluator.generate_lar_signals(
                symbol=sym,
                candles_df=candles_df,
                max_signals=0,
            )
            registered.extend(self._register_signals_by_direction(
                sym=sym,
                sigs=lar_sigs,
                quant_method=QuantMethod.LAR,
                trigger_state="liquidity_defense",
                min_sample_size=min_sample_size,
                min_win_rate=min_win_rate,
                min_z_score=1.50,
                now_ts=now_ts,
            ))

        return registered


if __name__ == "__main__":
    calibrator = SetupCalibrator()
    print("Starting comprehensive empirical calibration across all 5 quantitative methods (N >= 15)...")
    res = calibrator.run_calibration(min_sample_size=15)
    print(f"Calibration complete: {len(res)} verified bidirectional setups registered in SQLite.")
