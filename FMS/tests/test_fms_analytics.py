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
    # Create 30 synthetic bars
    bars = []
    for i in range(30):
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
    timestamps = [1700000000 + 5 * 14400, 1700000000 + 10 * 14400, 1700000000 + 15 * 14400]
    result = engine.evaluate_setup_excursions("EURUSD", SetupDirection.BUY, timestamps, df)
    assert result is not None
    assert result.sample_count == 3
    assert result.median_mfe_pips > 0
    assert result.recommended_tp_pips > 0
    assert result.recommended_sl_pips > 0
