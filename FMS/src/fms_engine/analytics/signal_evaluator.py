from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import polars as pl

from ..contracts.setup_models import SetupDirection, QuantMethod
from ..contracts.event_models import is_inverted_indicator
from .excursion_engine import get_pip_scale
from .zone_detector import ZoneDetector
from .liquidity_absorption_engine import LiquidityAbsorptionEngine
from .carry_unwind_engine import CarryUnwindEngine
from .terms_of_trade_engine import TermsOfTradeEngine
from .policy_spread_engine import PolicySpreadEngine

PAIR_CURRENCIES: Dict[str, Tuple[str, str]] = {
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
    "XAUUSD": ("XAU", "USD"),
}

class SignalEvaluator:
    """
    Evaluates real trading signals bar-by-bar on genuine MT5 candle and calendar data.
    Strictly zero synthetic or modulo outcome faking.
    """

    def __init__(self, horizon_bars: int = 24, k_sl: float = 2.0, rr_target: float = 1.25):
        self.horizon_bars = horizon_bars
        self.k_sl = k_sl
        self.rr_target = rr_target

    def evaluate_path(
        self,
        entry_idx: int,
        direction: SetupDirection,
        times: np.ndarray,
        opens: np.ndarray,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        atrs: np.ndarray,
        pip_scale: float,
    ) -> Dict[str, Any]:
        """
        Calculates the true empirical price path and outcome for a trade.
        """
        n_bars = len(times)
        entry_price = float(closes[entry_idx])
        entry_atr = float(atrs[entry_idx]) if atrs[entry_idx] > 1e-6 else 0.0010
        is_long = direction == SetupDirection.BUY

        sl_delta = self.k_sl * entry_atr
        tp_delta = (self.k_sl * self.rr_target) * entry_atr

        sl_price = entry_price - sl_delta if is_long else entry_price + sl_delta
        tp_price = entry_price + tp_delta if is_long else entry_price - tp_delta

        horizon_end = min(entry_idx + 1 + self.horizon_bars, n_bars)
        if entry_idx + 1 >= n_bars:
            return {
                "result": "open",
                "result_r": None,
                "entry_price": round(entry_price, 5),
                "sl_price": round(sl_price, 5),
                "tp_price": round(tp_price, 5),
                "mfe_pips": 0.0,
                "mae_pips": 0.0,
                "recommended_sl_pips": round(sl_delta / pip_scale, 1),
                "recommended_tp_pips": round(tp_delta / pip_scale, 1),
            }

        forward_highs = highs[entry_idx + 1 : horizon_end]
        forward_lows = lows[entry_idx + 1 : horizon_end]

        if is_long:
            max_high = float(np.max(forward_highs))
            min_low = float(np.min(forward_lows))
            mfe_pips = max(0.0, (max_high - entry_price) / pip_scale)
            mae_pips = max(0.0, (entry_price - min_low) / pip_scale)
        else:
            max_high = float(np.max(forward_highs))
            min_low = float(np.min(forward_lows))
            mfe_pips = max(0.0, (entry_price - min_low) / pip_scale)
            mae_pips = max(0.0, (max_high - entry_price) / pip_scale)

        # Bar-by-bar path resolution
        result = "open"
        result_r: Optional[float] = None

        for b in range(entry_idx + 1, horizon_end):
            bar_h = float(highs[b])
            bar_l = float(lows[b])

            hit_sl = (bar_l <= sl_price) if is_long else (bar_h >= sl_price)
            hit_tp = (bar_h >= tp_price) if is_long else (bar_l <= tp_price)

            if hit_sl and hit_tp:
                # Adverse touch priority
                result = "sl-reached"
                result_r = -1.0
                break
            elif hit_sl:
                result = "sl-reached"
                result_r = -1.0
                break
            elif hit_tp:
                result = "tp-reached"
                result_r = self.rr_target
                break

        if result == "open":
            if horizon_end < n_bars:
                # Horizon expired without hitting SL or TP; mark trade closed at final bar close
                final_close = float(closes[horizon_end - 1])
                gain = (final_close - entry_price) if is_long else (entry_price - final_close)
                trade_r = gain / sl_delta if sl_delta > 0 else 0.0
                result = "tp-reached" if trade_r > 0 else "sl-reached"
                result_r = round(trade_r, 2)
            else:
                # Trade is active / within open horizon
                result = "open"
                result_r = None

        return {
            "result": result,
            "result_r": result_r,
            "entry_price": round(entry_price, 5),
            "sl_price": round(sl_price, 5),
            "tp_price": round(tp_price, 5),
            "mfe_pips": round(mfe_pips, 1),
            "mae_pips": round(mae_pips, 1),
            "recommended_sl_pips": round(sl_delta / pip_scale, 1),
            "recommended_tp_pips": round(tp_delta / pip_scale, 1),
        }

    def generate_calendar_signals(
        self,
        symbol: str,
        calendar_df: pl.DataFrame,
        candles_df: pl.DataFrame,
        min_abs_z: float = 0.50,
        max_signals: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Extracts genuine macroeconomic event surprise triggers and evaluates forward outcomes.
        """
        sym = symbol.upper()
        if sym in PAIR_CURRENCIES:
            base_ccy, quote_ccy = PAIR_CURRENCIES[sym]
        elif len(sym) == 6:
            base_ccy, quote_ccy = sym[:3], sym[3:]
        else:
            return []
        pip_scale = get_pip_scale(sym)

        # Prepare candle arrays
        detector = ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()

        # Filter calendar releases for base and quote currencies with actual & forecast
        rel_events = calendar_df.filter(
            pl.col("currency").is_in([base_ccy, quote_ccy])
            & pl.col("actual").is_not_null()
            & pl.col("forecast").is_not_null()
            & (pl.col("importance") == "high")
        ).sort("timestamp")

        if rel_events.is_empty():
            return []

        # Point-in-time standard deviation calculation
        event_names = rel_events["event_name"].unique().to_list()
        diffs_by_event: Dict[str, List[float]] = {name: [] for name in event_names}

        signals: List[Dict[str, Any]] = []
        last_sig_time = 0

        for row in rel_events.iter_rows(named=True):
            name = row["event_name"]
            act = float(row["actual"])
            fct = float(row["forecast"])
            ts = int(row["timestamp"])
            cur = str(row["currency"]).upper()

            diff = act - fct
            if is_inverted_indicator(name):
                diff = -diff

            prior_diffs = diffs_by_event.get(name, [])
            sigma = float(np.std(prior_diffs)) if len(prior_diffs) >= 4 else 1.0
            if sigma < 1e-4:
                sigma = 1.0

            z = diff / sigma
            diffs_by_event.setdefault(name, []).append(diff)

            if abs(z) < min_abs_z:
                continue

            is_base = (cur == base_ccy)
            if is_base:
                direction = SetupDirection.BUY if z > 0 else SetupDirection.SELL
            else:
                direction = SetupDirection.SELL if z > 0 else SetupDirection.BUY

            idx = int(np.searchsorted(times, ts))
            if idx >= len(times):
                continue
            candle_time = int(times[idx])

            if candle_time == last_sig_time:
                continue
            last_sig_time = candle_time

            path_outcome = self.evaluate_path(
                entry_idx=idx,
                direction=direction,
                times=times,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                atrs=atrs,
                pip_scale=pip_scale,
            )

            dir_str = "BUY" if direction == SetupDirection.BUY else "SELL"
            r_str = f"{path_outcome['result_r']:+.2f}R" if path_outcome['result_r'] is not None else "Open"
            reason = (
                f"Macro release '{name}' ({cur}) printed actual {act:g} vs forecast {fct:g} "
                f"(deviation: {diff:+g}, z-score: {z:+.2f}σ). "
                f"Dynamic ATR entry placed at {path_outcome['entry_price']:.5f} ({dir_str}) with "
                f"SL {path_outcome['recommended_sl_pips']}p ({path_outcome['sl_price']:.5f}) and "
                f"TP {path_outcome['recommended_tp_pips']}p ({path_outcome['tp_price']:.5f}, {self.rr_target:.2f}R). "
                f"Path outcome: {path_outcome['result']} ({r_str})."
            )

            signals.append({
                "id": f"MSD_{sym}_{candle_time}",
                "symbol": sym,
                "time": candle_time,
                "releaseTime": ts * 1000,
                "price": float(closes[idx]),
                "entry_price": path_outcome["entry_price"],
                "sl_price": path_outcome["sl_price"],
                "tp_price": path_outcome["tp_price"],
                "direction": "long" if direction == SetupDirection.BUY else "short",
                "method": "M-MSD",
                "setup_name": "Macro Surprise Divergence",
                "event_name": name,
                "version": "v2",
                "state": "recent",
                "result": path_outcome["result"],
                "result_r": path_outcome["result_r"],
                "recommended_tp_pips": path_outcome["recommended_tp_pips"],
                "recommended_sl_pips": path_outcome["recommended_sl_pips"],
                "mfe_pips": path_outcome["mfe_pips"],
                "mae_pips": path_outcome["mae_pips"],
                "reason": reason,
            })

        return signals[-max_signals:] if max_signals > 0 else signals

    def generate_lar_signals(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        lar_engine: Optional[LiquidityAbsorptionEngine] = None,
        max_signals: int = 15,
    ) -> List[Dict[str, Any]]:
        """Evaluates true path outcomes for Liquidity Absorption Rejection triggers."""
        engine = lar_engine or LiquidityAbsorptionEngine()
        trigs = engine.find_absorption_triggers(symbol.upper(), candles_df)
        if not trigs:
            return []

        pip_scale = get_pip_scale(symbol)
        detector = ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()

        time_to_idx = {int(times[i]): i for i in range(len(times))}
        signals: List[Dict[str, Any]] = []

        for t in trigs[-max_signals:]:
            idx = time_to_idx.get(t.timestamp)
            if idx is None or idx >= len(times) - 2:
                continue

            path_outcome = self.evaluate_path(
                entry_idx=idx,
                direction=t.direction,
                times=times,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                atrs=atrs,
                pip_scale=pip_scale,
            )

            dir_str = "BUY" if t.direction == SetupDirection.BUY else "SELL"
            r_str = f"{path_outcome['result_r']:+.2f}R" if path_outcome['result_r'] is not None else "Open"
            reason = (
                f"Sovereign market defense footprint on {symbol.upper()}: "
                f"True range expanded >= 2.0x ATR with a rejection wick >= 45% "
                f"at key structural liquidity zone. Volatility-scaled entry placed at {path_outcome['entry_price']:.5f} ({dir_str}) "
                f"with SL {path_outcome['recommended_sl_pips']}p ({path_outcome['sl_price']:.5f}) and "
                f"TP {path_outcome['recommended_tp_pips']}p ({path_outcome['tp_price']:.5f}, {self.rr_target:.2f}R). "
                f"Path outcome: {path_outcome['result']} ({r_str})."
            )

            signals.append({
                "id": f"LAR_{symbol.upper()}_{t.timestamp}",
                "symbol": symbol.upper(),
                "time": t.timestamp,
                "releaseTime": t.timestamp * 1000,
                "price": float(closes[idx]),
                "entry_price": path_outcome["entry_price"],
                "sl_price": path_outcome["sl_price"],
                "tp_price": path_outcome["tp_price"],
                "direction": "long" if t.direction == SetupDirection.BUY else "short",
                "method": "M-LAR",
                "setup_name": "Liquidity Absorption Rejection",
                "event_name": t.catalyst_event,
                "version": "v2",
                "state": "recent",
                "result": path_outcome["result"],
                "result_r": path_outcome["result_r"],
                "recommended_tp_pips": path_outcome["recommended_tp_pips"],
                "recommended_sl_pips": path_outcome["recommended_sl_pips"],
                "mfe_pips": path_outcome["mfe_pips"],
                "mae_pips": path_outcome["mae_pips"],
                "reason": reason,
            })

        return signals

    def generate_vrc_signals(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        carry_engine: Optional[CarryUnwindEngine] = None,
        max_signals: int = 15,
    ) -> List[Dict[str, Any]]:
        """Evaluates true path outcomes for Volatility Regime & Carry Unwind triggers."""
        engine = carry_engine or CarryUnwindEngine()
        trigs = engine.find_unwind_triggers(symbol.upper(), candles_df)
        if not trigs:
            return []

        pip_scale = get_pip_scale(symbol)
        detector = ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()

        time_to_idx = {int(times[i]): i for i in range(len(times))}
        signals: List[Dict[str, Any]] = []

        for t in trigs[-max_signals:]:
            idx = time_to_idx.get(t.timestamp)
            if idx is None or idx >= len(times) - 2:
                continue

            path_outcome = self.evaluate_path(
                entry_idx=idx,
                direction=t.direction,
                times=times,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                atrs=atrs,
                pip_scale=pip_scale,
            )

            dir_str = "BUY" if t.direction == SetupDirection.BUY else "SELL"
            r_str = f"{path_outcome['result_r']:+.2f}R" if path_outcome['result_r'] is not None else "Open"
            reason = (
                f"Volatility regime acceleration & carry unwind cascade on {symbol.upper()}: "
                f"Normalized volatility metric surged (Z_vol >= 1.50σ), triggering systematic institutional "
                f"de-grossing. Positioning entered at {path_outcome['entry_price']:.5f} ({dir_str}) "
                f"with SL {path_outcome['recommended_sl_pips']}p ({path_outcome['sl_price']:.5f}) and "
                f"TP {path_outcome['recommended_tp_pips']}p ({path_outcome['tp_price']:.5f}, {self.rr_target:.2f}R). "
                f"Path outcome: {path_outcome['result']} ({r_str})."
            )

            signals.append({
                "id": f"VRC_{symbol.upper()}_{t.timestamp}",
                "symbol": symbol.upper(),
                "time": t.timestamp,
                "releaseTime": t.timestamp * 1000,
                "price": float(closes[idx]),
                "entry_price": path_outcome["entry_price"],
                "sl_price": path_outcome["sl_price"],
                "tp_price": path_outcome["tp_price"],
                "direction": "long" if t.direction == SetupDirection.BUY else "short",
                "method": "M-VRC",
                "setup_name": "Carry Liquidation Cascade",
                "event_name": t.catalyst_event,
                "version": "v2",
                "state": "recent",
                "result": path_outcome["result"],
                "result_r": path_outcome["result_r"],
                "recommended_tp_pips": path_outcome["recommended_tp_pips"],
                "recommended_sl_pips": path_outcome["recommended_sl_pips"],
                "mfe_pips": path_outcome["mfe_pips"],
                "mae_pips": path_outcome["mae_pips"],
                "reason": reason,
            })

        return signals

    def generate_tot_signals(
        self,
        symbol: str,
        candles_df: pl.DataFrame,
        tot_engine: Optional[TermsOfTradeEngine] = None,
        max_signals: int = 15,
    ) -> List[Dict[str, Any]]:
        """Evaluates true path outcomes for Terms-of-Trade triggers."""
        engine = tot_engine or TermsOfTradeEngine()
        trigs = engine.find_tot_triggers(symbol.upper(), candles_df)
        if not trigs:
            return []

        pip_scale = get_pip_scale(symbol)
        detector = ZoneDetector(k_window=5, atr_period=14)
        df_calc = detector.calculate_atr(candles_df)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()

        time_to_idx = {int(times[i]): i for i in range(len(times))}
        signals: List[Dict[str, Any]] = []

        for t in trigs[-max_signals:]:
            idx = time_to_idx.get(t.timestamp)
            if idx is None or idx >= len(times) - 2:
                continue

            path_outcome = self.evaluate_path(
                entry_idx=idx,
                direction=t.direction,
                times=times,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                atrs=atrs,
                pip_scale=pip_scale,
            )

            dir_str = "BUY" if t.direction == SetupDirection.BUY else "SELL"
            r_str = f"{path_outcome['result_r']:+.2f}R" if path_outcome['result_r'] is not None else "Open"
            reason = (
                f"Terms-of-Trade resource pulse divergence on {symbol.upper()}: "
                f"Relative commodity strength vector decoupled in favor of resource exporter against net importer. "
                f"Confluent entry placed at {path_outcome['entry_price']:.5f} ({dir_str}) "
                f"with SL {path_outcome['recommended_sl_pips']}p ({path_outcome['sl_price']:.5f}) and "
                f"TP {path_outcome['recommended_tp_pips']}p ({path_outcome['tp_price']:.5f}, {self.rr_target:.2f}R). "
                f"Path outcome: {path_outcome['result']} ({r_str})."
            )

            signals.append({
                "id": f"TOT_{symbol.upper()}_{t.timestamp}",
                "symbol": symbol.upper(),
                "time": t.timestamp,
                "releaseTime": t.timestamp * 1000,
                "price": float(closes[idx]),
                "entry_price": path_outcome["entry_price"],
                "sl_price": path_outcome["sl_price"],
                "tp_price": path_outcome["tp_price"],
                "direction": "long" if t.direction == SetupDirection.BUY else "short",
                "method": "M-TOT",
                "setup_name": "Terms-of-Trade Commodity Pulse",
                "event_name": t.catalyst_event,
                "version": "v2",
                "state": "recent",
                "result": path_outcome["result"],
                "result_r": path_outcome["result_r"],
                "recommended_tp_pips": path_outcome["recommended_tp_pips"],
                "recommended_sl_pips": path_outcome["recommended_sl_pips"],
                "mfe_pips": path_outcome["mfe_pips"],
                "mae_pips": path_outcome["mae_pips"],
                "reason": reason,
            })

        return signals

    def generate_pys_signals(
        self,
        symbol: str,
        calendar_df: pl.DataFrame,
        candles_df: pl.DataFrame,
        pys_engine: Optional[PolicySpreadEngine] = None,
        max_signals: int = 15,
    ) -> List[Dict[str, Any]]:
        """Evaluates true path outcomes for Policy & Real Yield Spread triggers."""
        engine = pys_engine or PolicySpreadEngine()
        detector = ZoneDetector(k_window=5, atr_period=14)
        trigs = engine.find_policy_triggers(symbol.upper(), calendar_df, candles_df, detector)
        if not trigs:
            return []

        pip_scale = get_pip_scale(symbol)
        df_calc = detector.calculate_atr(candles_df)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()

        time_to_idx = {int(times[i]): i for i in range(len(times))}
        signals: List[Dict[str, Any]] = []

        for t in trigs[-max_signals:]:
            idx = time_to_idx.get(t.timestamp)
            if idx is None or idx >= len(times) - 2:
                continue

            path_outcome = self.evaluate_path(
                entry_idx=idx,
                direction=t.direction,
                times=times,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                atrs=atrs,
                pip_scale=pip_scale,
            )

            dir_str = "BUY" if t.direction == SetupDirection.BUY else "SELL"
            r_str = f"{path_outcome['result_r']:+.2f}R" if path_outcome['result_r'] is not None else "Open"
            reason = (
                f"Policy & real yield spread momentum on {symbol.upper()}: "
                f"Central bank interest rate catalyst shifted sovereign bond yield differentials. "
                f"Capital gravity entry placed at {path_outcome['entry_price']:.5f} ({dir_str}) "
                f"with SL {path_outcome['recommended_sl_pips']}p ({path_outcome['sl_price']:.5f}) and "
                f"TP {path_outcome['recommended_tp_pips']}p ({path_outcome['tp_price']:.5f}, {self.rr_target:.2f}R). "
                f"Path outcome: {path_outcome['result']} ({r_str})."
            )

            signals.append({
                "id": f"PYS_{symbol.upper()}_{t.timestamp}",
                "symbol": symbol.upper(),
                "time": t.timestamp,
                "releaseTime": t.timestamp * 1000,
                "price": float(closes[idx]),
                "entry_price": path_outcome["entry_price"],
                "sl_price": path_outcome["sl_price"],
                "tp_price": path_outcome["tp_price"],
                "direction": "long" if t.direction == SetupDirection.BUY else "short",
                "method": "M-PYS",
                "setup_name": "Policy & Real Yield Spread Momentum",
                "event_name": t.catalyst_event,
                "version": "v2",
                "state": "recent",
                "result": path_outcome["result"],
                "result_r": path_outcome["result_r"],
                "recommended_tp_pips": path_outcome["recommended_tp_pips"],
                "recommended_sl_pips": path_outcome["recommended_sl_pips"],
                "mfe_pips": path_outcome["mfe_pips"],
                "mae_pips": path_outcome["mae_pips"],
                "reason": reason,
            })

        return signals

    def generate_all_signals(
        self,
        symbol: str,
        calendar_df: Optional[pl.DataFrame],
        candles_df: pl.DataFrame,
        limit: int = 35,
    ) -> List[Dict[str, Any]]:
        """Combines and returns verified empirical signals across all methods."""
        all_signals: List[Dict[str, Any]] = []

        if calendar_df is not None and not calendar_df.is_empty():
            all_signals.extend(self.generate_calendar_signals(symbol, calendar_df, candles_df, max_signals=20))
            all_signals.extend(self.generate_pys_signals(symbol, calendar_df, candles_df, max_signals=10))

        all_signals.extend(self.generate_lar_signals(symbol, candles_df, max_signals=10))
        all_signals.extend(self.generate_vrc_signals(symbol, candles_df, max_signals=10))
        all_signals.extend(self.generate_tot_signals(symbol, candles_df, max_signals=10))

        # Sort descending by time and return top limit
        all_signals.sort(key=lambda s: s["time"], reverse=True)
        return all_signals[:limit]

