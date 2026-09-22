import pytest
import numpy as np
import polars as pl
from fms_engine.contracts.event_models import MacroState, EventFamily
from fms_engine.contracts.setup_models import SetupDirection
from fms_engine.analytics.surprise_engine import SurpriseEngine
from fms_engine.analytics.zone_detector import ZoneDetector
from fms_engine.analytics.excursion_engine import ExcursionEngine

def test_surprise_engine_evaluations():
    engine = SurpriseEngine()
    engine.std_cache["US Non-Farm Payrolls"] = 50.0  # 50k std

    # Test Full Acceleration (Beat consensus and previous)
    surprise, momentum, z, state = engine.evaluate_release(
        actual=250.0,
        forecast=180.0,
        previous=150.0,
        event_name="US Non-Farm Payrolls",
        family=EventFamily.LABOR,
    )
    assert surprise == 70.0
    assert momentum == 100.0
    assert z == 1.4
    assert state == MacroState.FULL_ACCELERATION

    # Test Full Deceleration (Missed consensus and deteriorated)
    surprise, momentum, z, state = engine.evaluate_release(
        actual=120.0,
        forecast=180.0,
        previous=150.0,
        event_name="US Non-Farm Payrolls",
        family=EventFamily.LABOR,
    )
    assert surprise == -60.0
    assert momentum == -30.0
    assert z == -1.2
    assert state == MacroState.FULL_DECELERATION

    # Test Conflicted (Beat consensus but worse than previous)
    surprise, momentum, z, state = engine.evaluate_release(
        actual=200.0,
        forecast=180.0,
        previous=220.0,
        event_name="US Non-Farm Payrolls",
        family=EventFamily.LABOR,
    )
    assert surprise == 20.0
    assert momentum == -20.0
    assert state == MacroState.CONFLICTED

    # Test In-Line (Small shock)
    surprise, momentum, z, state = engine.evaluate_release(
        actual=182.0,
        forecast=180.0,
        previous=180.0,
        event_name="US Non-Farm Payrolls",
        family=EventFamily.LABOR,
    )
    assert abs(z) < 0.25
    assert state == MacroState.IN_LINE

def test_zone_detector():
    detector = ZoneDetector(k_window=2, atr_period=5)
    # Create 20 synthetic bars with a clear pivot high at index 10 and pivot low at index 15
    prices = [1.1000 + i * 0.0010 for i in range(10)] + [1.1150] + [1.1100 - i * 0.0015 for i in range(10)]
    bars = []
    for i, p in enumerate(prices):
        bars.append({
            "time": 1700000000 + i * 14400,
            "open": p - 0.0002,
            "high": p + 0.0010,
            "low": p - 0.0010,
            "close": p + 0.0001,
            "tick_volume": 100,
            "spread": 1,
        })
    df = pl.DataFrame(bars)
    zones = detector.detect_zones(df)
    assert len(zones) >= 1
    assert any(z.zone_type == "resistance" for z in zones)

def test_excursion_engine():
    engine = ExcursionEngine(max_bars=10)
    # Create 50 synthetic bars for robust ATR calibration
    bars = []
    for i in range(50):
        bars.append({
            "time": 1700000000 + i * 14400,
            "open": 1.1000 + i * 0.0005,
            "high": 1.1000 + i * 0.0005 + 0.0020,
            "low": 1.1000 + i * 0.0005 - 0.0010,
            "close": 1.1000 + i * 0.0005 + 0.0003,
            "tick_volume": 100,
            "spread": 1,
        })
    df = pl.DataFrame(bars)
    timestamps = [1700000000 + 15 * 14400, 1700000000 + 20 * 14400, 1700000000 + 25 * 14400]
    result = engine.evaluate_setup_excursions("EURUSD", SetupDirection.BUY, timestamps, df)
    assert result is not None
    assert result.sample_count == 3
    assert result.median_mfe_pips > 0
    assert result.recommended_tp_pips > 0
    assert result.recommended_sl_pips > 0

def test_macro_divergence_engine():
    from fms_engine.analytics.macro_divergence_engine import MacroDivergenceEngine

    surprise_engine = SurpriseEngine()
    surprise_engine.std_cache["US Non-Farm Payrolls"] = 50.0
    surprise_engine.std_cache["Eurozone Harmonised CPI YoY"] = 0.2

    cal_data = [
        # USD misses heavily
        {
            "event_id": "1",
            "event_name": "US Non-Farm Payrolls",
            "currency": "USD",
            "family": "labor",
            "timestamp": 1700000000,
            "actual": 80.0,
            "forecast": 180.0,
            "previous": 150.0,
            "impact": "high",
        },
        # EUR beats strongly
        {
            "event_id": "2",
            "event_name": "Eurozone Harmonised CPI YoY",
            "currency": "EUR",
            "family": "inflation",
            "timestamp": 1700000100,
            "actual": 3.4,
            "forecast": 3.0,
            "previous": 3.0,
            "impact": "high",
        },
    ]
    cal_df = pl.DataFrame(cal_data)
    engine = MacroDivergenceEngine(lookback_days=14, min_divergence_z=1.50)

    events_scored = engine.compute_currency_scores(cal_df, surprise_engine)
    assert len(events_scored) == 2

    triggers = engine.find_divergence_triggers("EURUSD", events_scored)
    assert len(triggers) >= 1
    # EUR beat (+2.0 std) and USD miss (-2.0 std) -> EUR - USD = +4.0 std -> BUY trigger
    assert triggers[0].direction == SetupDirection.BUY
    assert triggers[0].spread_z >= 1.50

def test_policy_spread_engine():
    from fms_engine.analytics.policy_spread_engine import PolicySpreadEngine
    from fms_engine.contracts.setup_models import SetupDirection

    cal_data = [
        # USD Fed rate at 5.0%
        {
            "event_id": "1",
            "event_name": "Federal Reserve Interest Rate Decision",
            "currency": "USD",
            "family": "monetary_policy",
            "timestamp": 1700000000,
            "actual": 5.0,
            "forecast": 5.0,
            "previous": 4.75,
            "impact": "high",
        },
        # US CPI at 3.0%
        {
            "event_id": "2",
            "event_name": "US Consumer Price Index (CPI) YoY",
            "currency": "USD",
            "family": "inflation",
            "timestamp": 1700000100,
            "actual": 3.0,
            "forecast": 3.0,
            "previous": 3.2,
            "impact": "high",
        },
        # JPY BoJ rate at -0.10%
        {
            "event_id": "3",
            "event_name": "Bank of Japan Interest Rate Decision",
            "currency": "JPY",
            "family": "monetary_policy",
            "timestamp": 1700000200,
            "actual": -0.10,
            "forecast": -0.10,
            "previous": -0.10,
            "impact": "high",
        },
        # Japan CPI at 2.0%
        {
            "event_id": "4",
            "event_name": "Japan National Core CPI YoY",
            "currency": "JPY",
            "family": "inflation",
            "timestamp": 1700000300,
            "actual": 2.0,
            "forecast": 2.0,
            "previous": 2.2,
            "impact": "high",
        },
    ]
    cal_df = pl.DataFrame(cal_data)
    engine = PolicySpreadEngine(min_real_spread_bps=100.0, refractory_bars=1)

    # Synthetic candles for USDJPY
    candles_data = [
        {"time": 1700000000 + i * 14400, "open": 140.0, "high": 140.5, "low": 139.8, "close": 140.2, "tick_volume": 100, "spread": 2}
        for i in range(10)
    ]
    candles_df = pl.DataFrame(candles_data)

    triggers = engine.find_policy_triggers("USDJPY", cal_df, candles_df)
    assert len(triggers) >= 1
    # USD real yield: 5.0 - 3.0 = +2.0%, JPY real yield: -0.10 - 2.0 = -2.10%
    # Real spread = +2.0 - (-2.10) = +4.10% -> USDJPY BUY
    assert triggers[0].direction == SetupDirection.BUY
    assert triggers[0].real_spread > 1.0

def test_library_models_contract():
    from fms_engine.contracts.library_models import MethodSectionContract, LibrarySummaryContract, AccordionState
    from fms_engine.contracts.setup_models import QuantMethod

    section = MethodSectionContract(
        method_id=QuantMethod.PYS,
        name="Policy & Real Yield Spread Momentum",
        code="M-PYS",
        description="Captures sovereign interest rate differentials and real yield momentum.",
        hypothesis="Capital flows gravitate to currencies with positive real purchasing power expansion.",
        research_chapter_file="10-policy-and-real-yield-spread-momentum.md",
        setup_count=8,
        aggregate_net_r=137.10,
        average_expectancy_r=0.233,
        average_win_rate=0.565,
        ui_accordion_state=AccordionState.EXPANDED,
    )
    assert section.setup_count == 8
    assert section.aggregate_net_r > 100.0

    summary = LibrarySummaryContract(
        methods=[section],
        total_setups=8,
        total_net_r=137.10,
        average_portfolio_expectancy=0.233,
        last_audit_timestamp=1700000000,
    )
    assert summary.total_setups == 8

def test_portal_endpoint():
    from fms_engine.api.app import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "FMS Library" in response.text
    assert "Codified Setups" in response.text

def test_terms_of_trade_engine():
    from fms_engine.analytics.terms_of_trade_engine import TermsOfTradeEngine

    engine = TermsOfTradeEngine(min_pulse_threshold=1.00, refractory_bars=2)
    # Synthetic candles for AUDJPY with an upward pulse in AUD vs JPY (100 bars)
    candles_data = []
    base_price = 80.0
    for i in range(100):
        # Push strong upward momentum in AUDJPY
        inc = 0.10 * i if 30 <= i <= 50 else 0.01 * i
        candles_data.append({
            "time": 1700000000 + i * 14400,
            "open": base_price + inc,
            "high": base_price + inc + 0.30,
            "low": base_price + inc - 0.10,
            "close": base_price + inc + 0.25,
            "tick_volume": 100,
            "spread": 2,
        })
    candles_df = pl.DataFrame(candles_data)
    triggers = engine.find_tot_triggers("AUDJPY", candles_df)
    assert len(triggers) >= 1
    assert any(t.direction == SetupDirection.BUY for t in triggers)
    assert any(t.tot_pulse >= 1.0 for t in triggers)

def test_carry_unwind_engine():
    from fms_engine.analytics.carry_unwind_engine import CarryUnwindEngine

    engine = CarryUnwindEngine(lookback_baseline=20, min_vol_z=1.50, refractory_bars=2)
    # Synthetic candles (100 bars) with normal variance then a volatility shock
    candles_data = []
    base_price = 140.0
    for i in range(100):
        if i == 35:
            # Massive volatility expansion shock (Carry Unwind)
            candles_data.append({
                "time": 1700000000 + i * 14400,
                "open": base_price,
                "high": base_price + 4.00,
                "low": base_price - 4.00,
                "close": base_price - 2.00,
                "tick_volume": 500,
                "spread": 5,
            })
        else:
            var = (i % 5) * 0.05
            candles_data.append({
                "time": 1700000000 + i * 14400,
                "open": base_price,
                "high": base_price + 0.10 + var,
                "low": base_price - 0.10 - var,
                "close": base_price,
                "tick_volume": 100,
                "spread": 2,
            })
    candles_df = pl.DataFrame(candles_data)
    triggers = engine.find_unwind_triggers("USDJPY", candles_df)
    assert len(triggers) >= 1
    assert triggers[0].direction == SetupDirection.SELL
    assert triggers[0].volatility_z >= 1.50

def test_liquidity_absorption_engine():
    from fms_engine.analytics.liquidity_absorption_engine import LiquidityAbsorptionEngine

    engine = LiquidityAbsorptionEngine(min_expansion_ratio=1.50, min_wick_ratio=0.40, refractory_bars=2)
    # Synthetic candles (100 bars): normal baseline, explosive pin bar rejection at index 35
    candles_data = []
    base_price = 150.0
    for i in range(100):
        if i == 35:
            # The BoJ Shock candle: Open=151.0, High=155.0, Low=150.5, Close=151.2
            # Range = 4.5, Upper wick = 155.0 - 151.2 = 3.8 (84% wick)
            candles_data.append({
                "time": 1700000000 + i * 14400,
                "open": 151.0,
                "high": 155.0,
                "low": 150.5,
                "close": 151.2,
                "tick_volume": 1000,
                "spread": 5,
            })
        else:
            var = (i % 5) * 0.02
            candles_data.append({
                "time": 1700000000 + i * 14400,
                "open": base_price,
                "high": base_price + 0.15 + var,
                "low": base_price - 0.15 - var,
                "close": base_price,
                "tick_volume": 100,
                "spread": 2,
            })
    candles_df = pl.DataFrame(candles_data)
    triggers = engine.find_absorption_triggers("USDJPY", candles_df)
    assert len(triggers) >= 1
    assert triggers[0].direction == SetupDirection.SELL
    assert triggers[0].expansion_ratio >= 1.50
    assert triggers[0].wick_ratio >= 0.40




