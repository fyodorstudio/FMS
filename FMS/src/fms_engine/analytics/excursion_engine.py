from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
import polars as pl
from ..contracts.event_models import MacroReleaseDTO, MacroState
from ..contracts.setup_models import SetupDirection
from ..config import settings
from .zone_detector import ZoneDetector

def get_pip_scale(symbol: str) -> float:
    """Returns the price delta corresponding to 1 pip."""
    sym = symbol.upper()
    if "JPY" in sym:
        return 0.01
    if "XAU" in sym or "GOLD" in sym:
        return 0.10
    if "BTC" in sym or "CRYPTO" in sym:
        return 1.00
    return 0.0001

@dataclass
class ExcursionResult:
    sample_count: int
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
    atr_median_pips: float = 50.0

class ExcursionEngine:
    """
    Vectorized calculation of Maximum Adverse & Favorable Excursions (MAE/MFE)
    with ATR-normalized dynamic volatility scaling, path-dependent survival analysis,
    and cumulative R accounting across multi-year market regimes.
    """

    def __init__(self, max_bars: int = 24, atr_period: int = 14):
        self.max_bars = max_bars
        self.atr_period = atr_period

    def evaluate_setup_excursions(
        self,
        symbol: str,
        direction: SetupDirection,
        event_timestamps: List[int],
        candles: pl.DataFrame,
        k_sl_fixed: Optional[float] = None,
        rr_fixed: Optional[float] = None,
    ) -> Optional[ExcursionResult]:
        """Calculates statistical MAE, MFE, and optimal ATR-adaptive SL/TP across historical events."""
        if candles.is_empty() or len(candles) < 20 or not event_timestamps:
            return None

        # Ensure ATR is calculated
        if "atr" not in candles.columns:
            detector = ZoneDetector(k_window=5, atr_period=self.atr_period)
            df_calc = detector.calculate_atr(candles)
        else:
            df_calc = candles

        pip_scale = get_pip_scale(symbol)
        times = df_calc["time"].to_numpy()
        opens = df_calc["open"].to_numpy()
        highs = df_calc["high"].to_numpy()
        lows = df_calc["low"].to_numpy()
        closes = df_calc["close"].to_numpy()
        atrs = df_calc["atr"].to_numpy()
        n_bars = len(times)

        mfes_pips: List[float] = []
        maes_pips: List[float] = []
        mfes_atr: List[float] = []
        maes_atr: List[float] = []
        valid_indices: List[int] = []
        is_long = direction == SetupDirection.BUY

        min_allowed_idx = min(self.atr_period, 5)

        for ts in event_timestamps:
            idx = int(np.searchsorted(times, ts))
            if idx >= n_bars - 2 or idx < min_allowed_idx:
                continue

            entry_price = float(opens[idx])
            entry_atr = float(atrs[idx])
            if entry_atr <= 1e-6:
                entry_atr = float(np.median(atrs[atrs > 0])) if np.any(atrs > 0) else 0.0010

            horizon_end = min(idx + self.max_bars, n_bars)
            future_highs = highs[idx:horizon_end]
            future_lows = lows[idx:horizon_end]

            if is_long:
                max_high = float(np.max(future_highs))
                min_low = float(np.min(future_lows))
                mfe_price = max(0.0, max_high - entry_price)
                mae_price = max(0.0, entry_price - min_low)
            else:
                max_high = float(np.max(future_highs))
                min_low = float(np.min(future_lows))
                mfe_price = max(0.0, entry_price - min_low)
                mae_price = max(0.0, max_high - entry_price)

            mfe_pips = mfe_price / pip_scale
            mae_pips = mae_price / pip_scale
            mfe_atr = mfe_price / entry_atr
            mae_atr = mae_price / entry_atr

            mfes_pips.append(mfe_pips)
            maes_pips.append(mae_pips)
            mfes_atr.append(mfe_atr)
            maes_atr.append(mae_atr)
            valid_indices.append(idx)

        if len(valid_indices) < 3:
            return None

        median_mfe_pips = float(np.median(mfes_pips))
        mae_85_pips = float(np.percentile(maes_pips, settings.mae_percentile * 100))
        valid_atrs = [atrs[i] / pip_scale for i in valid_indices if atrs[i] > 1e-6]
        median_atr_pips = float(np.median(valid_atrs)) if valid_atrs else 50.0

        # Parametric simulation to find optimal risk-adjusted parameter set
        candidate_ks = [k_sl_fixed] if k_sl_fixed is not None else [1.5, 2.0, 2.5]
        candidate_rrs = [rr_fixed] if rr_fixed is not None else [1.0, 1.25, 1.50]

        best_score = -999.0
        best_result: Optional[Tuple] = None

        for k_sl in candidate_ks:
            for rr_target in candidate_rrs:
                wins = 0
                losses = 0
                r_multiples: List[float] = []
                holding_bars_list: List[int] = []

                for idx in valid_indices:
                    entry_price = float(opens[idx])
                    entry_atr = float(atrs[idx])
                    if entry_atr <= 1e-6:
                        entry_atr = float(np.median(atrs[atrs > 0])) if np.any(atrs > 0) else 0.0010

                    sl_delta = k_sl * entry_atr
                    tp_delta = (k_sl * rr_target) * entry_atr

                    if is_long:
                        sl_price = entry_price - sl_delta
                        tp_price = entry_price + tp_delta
                    else:
                        sl_price = entry_price + sl_delta
                        tp_price = entry_price - tp_delta

                    resolved = False
                    horizon_end = min(idx + self.max_bars, n_bars)

                    for step, b in enumerate(range(idx, horizon_end)):
                        bar_h = float(highs[b])
                        bar_l = float(lows[b])

                        hit_sl = (bar_l <= sl_price) if is_long else (bar_h >= sl_price)
                        hit_tp = (bar_h >= tp_price) if is_long else (bar_l <= tp_price)

                        # Conservative tie-breaker: assume adverse touch first
                        if hit_sl and hit_tp:
                            losses += 1
                            r_multiples.append(-1.0)
                            holding_bars_list.append(step + 1)
                            resolved = True
                            break
                        elif hit_sl:
                            losses += 1
                            r_multiples.append(-1.0)
                            holding_bars_list.append(step + 1)
                            resolved = True
                            break
                        elif hit_tp:
                            wins += 1
                            r_multiples.append(rr_target)
                            holding_bars_list.append(step + 1)
                            resolved = True
                            break

                    if not resolved:
                        final_close = float(closes[horizon_end - 1])
                        trade_gain = (final_close - entry_price) if is_long else (entry_price - final_close)
                        trade_r = trade_gain / sl_delta if sl_delta > 0 else 0.0
                        r_multiples.append(trade_r)
                        if trade_r > 0:
                            wins += 1
                        else:
                            losses += 1
                        holding_bars_list.append(horizon_end - idx)

                total_runs = len(valid_indices)
                win_rate = wins / total_runs if total_runs > 0 else 0.0
                net_r = float(np.sum(r_multiples)) if r_multiples else 0.0
                ev_per_trade = float(np.mean(r_multiples)) if r_multiples else 0.0
                avg_hold = float(np.mean(holding_bars_list)) if holding_bars_list else 0.0

                # Score prioritization: reward positive EV and win rates >= 50%
                score = ev_per_trade if win_rate >= 0.50 else (ev_per_trade - 1.0)

                if score > best_score:
                    best_score = score
                    best_result = (
                        total_runs, wins, losses, win_rate,
                        k_sl, rr_target, net_r, ev_per_trade, avg_hold
                    )

        if best_result is None:
            return None

        tot, w, l, wr, chosen_k_sl, chosen_rr, net_r_val, ev_val, hold_val = best_result

        # Calculate representative pips for setup registration / UI display based on median ATR
        rep_sl_pips = round(chosen_k_sl * median_atr_pips, 1)
        rep_tp_pips = round((chosen_k_sl * chosen_rr) * median_atr_pips, 1)

        # Expectancy gate: win rate >= 50%, Net R > 0, R:R >= 1.0, minimum 8 occurrences
        valid_edge = wr >= 0.50 and net_r_val > 0.0 and chosen_rr >= 1.0 and tot >= 8

        return ExcursionResult(
            sample_count=tot,
            win_count=w,
            loss_count=l,
            respect_rate=round(wr, 2),
            median_mfe_pips=round(median_mfe_pips, 1),
            mae_85_pips=round(mae_85_pips, 1),
            recommended_sl_pips=rep_sl_pips,
            recommended_tp_pips=rep_tp_pips,
            reward_risk_ratio=round(chosen_rr, 2),
            avg_holding_bars=round(hold_val, 1),
            net_realized_r=round(net_r_val, 1),
            expected_r_per_trade=round(ev_val, 2),
            valid_edge=valid_edge,
            k_sl=chosen_k_sl,
            atr_median_pips=round(median_atr_pips, 1),
        )
