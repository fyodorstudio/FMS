"""
Unit Tests for the Deterministic Macroeconomic Scoring Engine.
Run with standard python: python -m unittest FMS/scoring_system/test_scoring_engine.py
"""

import unittest
from FMS.scoring_system.models import EventFamily, MacroReleaseInput, MacroState
from FMS.scoring_system.surprise_momentum_engine import SurpriseMomentumEngine


class TestSurpriseMomentumEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SurpriseMomentumEngine(z_threshold=0.25, default_sigma=0.20)

    def test_strong_beat_full_acceleration(self):
        # US Core CPI: Actual 3.6% vs Forecast 3.2% vs Previous 3.3%
        # Surprise = +0.40, Momentum = +0.30 -> Full Acceleration
        release = MacroReleaseInput(
            event_name="US Core CPI YoY",
            currency="USD",
            actual=3.6,
            forecast=3.2,
            previous=3.3,
            family=EventFamily.INFLATION,
        )
        res = self.engine.score(release)
        self.assertEqual(res.raw_surprise, 0.4)
        self.assertEqual(res.raw_momentum, 0.3)
        self.assertGreater(res.z_score, 0.25)
        self.assertEqual(res.state, MacroState.FULL_ACCELERATION)
        self.assertFalse(res.is_inverted)

    def test_conflicted_beat_but_momentum_negative(self):
        # Beat forecast (2.5% vs 2.2%), but lower than previous (2.8%)
        # Surprise > 0, Momentum < 0 -> Conflicted
        release = MacroReleaseInput(
            event_name="US Retail Sales MoM",
            currency="USD",
            actual=2.5,
            forecast=2.2,
            previous=2.8,
            family=EventFamily.GROWTH,
        )
        res = self.engine.score(release)
        self.assertGreater(res.raw_surprise, 0)
        self.assertLess(res.raw_momentum, 0)
        self.assertEqual(res.state, MacroState.CONFLICTED)

    def test_inverted_indicator_unemployment_drop(self):
        # Unemployment Rate: Actual 3.8% vs Forecast 4.1% vs Previous 4.0%
        # Raw surprise is -0.3% (lower unemployment is good for currency).
        # Effective surprise should be inverted to +0.3% -> Full Acceleration
        release = MacroReleaseInput(
            event_name="US Unemployment Rate",
            currency="USD",
            actual=3.8,
            forecast=4.1,
            previous=4.0,
            family=EventFamily.LABOR,
        )
        res = self.engine.score(release)
        self.assertTrue(res.is_inverted)
        self.assertEqual(res.raw_surprise, -0.3)
        self.assertEqual(res.effective_surprise, 0.3)
        self.assertGreater(res.z_score, 0)
        self.assertEqual(res.state, MacroState.FULL_ACCELERATION)

    def test_in_line_release(self):
        # Small discrepancy within noise threshold: Actual 50.1 vs Forecast 50.0
        # Surprise = 0.1, with sigma = 1.0 -> Z = 0.1 <= 0.25 threshold -> IN_LINE
        engine_large_sigma = SurpriseMomentumEngine(z_threshold=0.25, default_sigma=1.0)
        release = MacroReleaseInput(
            event_name="ISM Manufacturing PMI",
            currency="USD",
            actual=50.1,
            forecast=50.0,
            previous=49.8,
            family=EventFamily.SENTIMENT,
        )
        res = engine_large_sigma.score(release)
        self.assertEqual(res.state, MacroState.IN_LINE)

    def test_calibration_from_historical_data(self):
        # Feed 4 observations with surprise variance
        observations = [
            ("US CPI MoM", 0.4, 0.2),  # diff = +0.2
            ("US CPI MoM", 0.1, 0.2),  # diff = -0.1
            ("US CPI MoM", 0.3, 0.2),  # diff = +0.1
            ("US CPI MoM", 0.0, 0.2),  # diff = -0.2
        ]
        self.engine.calibrate_from_observations(observations)
        self.assertIn("US CPI MoM", self.engine.std_cache)
        self.assertAlmostEqual(self.engine.std_cache["US CPI MoM"], 0.18257, places=4)


if __name__ == "__main__":
    unittest.main()
