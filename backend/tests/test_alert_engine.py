import unittest
import uuid
from datetime import date, datetime, timezone

from app.models.spatial import AlertSeverity, SatelliteSnapshot
from app.services.alert_engine import (
    AlertEngine,
    AlertThresholds,
    TelemetryObservation,
)

class TestAlertEngine(unittest.TestCase):
    """Unit tests for multi-sensor NDVI + SAR early-warning signal detection."""

    def setUp(self) -> None:
        self.engine = AlertEngine()

    def _obs(
        self,
        day: int,
        ndvi: float | None = 0.65,
        vv: float | None = -11.5,
        vh: float | None = -17.5,
        quality: float = 0.95,
    ) -> TelemetryObservation:
        return TelemetryObservation(
            observation_date=datetime(2026, 6, day, tzinfo=timezone.utc),
            ndvi_mean=ndvi,
            sar_vv_db=vv,
            sar_vh_db=vh,
            valid_pixel_ratio=quality,
        )

    def test_baseline_stable_returns_green(self) -> None:
        baseline = [self._obs(1, ndvi=0.68, vv=-11.8), self._obs(5, ndvi=0.66, vv=-11.6)]
        recent = [self._obs(20, ndvi=0.64, vv=-11.4), self._obs(25, ndvi=0.63, vv=-11.5)]

        result = self.engine.evaluate(baseline, recent)
        self.assertEqual(result.severity, AlertSeverity.GREEN)
        self.assertEqual(result.signal_type, "BASELINE_STABLE")
        self.assertGreaterEqual(result.confidence_score, 0.75)

    def test_land_clearing_ndvi_drop_returns_amber(self) -> None:
        # Vegetation drops ~55% (e.g. topsoil stripped), SAR stays flat
        baseline = [self._obs(1, ndvi=0.70, vv=-12.0), self._obs(5, ndvi=0.68, vv=-11.8)]
        recent = [self._obs(20, ndvi=0.31, vv=-11.9), self._obs(25, ndvi=0.29, vv=-12.1)]

        result = self.engine.evaluate(baseline, recent)
        self.assertEqual(result.severity, AlertSeverity.AMBER)
        self.assertEqual(result.signal_type, "LAND_CLEARING")
        self.assertLess(result.ndvi_delta_pct, -50.0)
        self.assertGreaterEqual(result.confidence_score, 0.80)

    def test_structural_expansion_sar_spike_returns_amber(self) -> None:
        # Brownfield / concrete lot (low NDVI already) where steel warehouse structure rises (+3.6 dB VV)
        baseline = [self._obs(1, ndvi=0.22, vv=-12.2, vh=-18.0)]
        recent = [self._obs(20, ndvi=0.20, vv=-8.6, vh=-15.4)]

        result = self.engine.evaluate(baseline, recent)
        self.assertEqual(result.severity, AlertSeverity.AMBER)
        self.assertEqual(result.signal_type, "STRUCTURAL_EXPANSION")
        self.assertAlmostEqual(result.sar_vv_delta_db, 3.6, places=2)

    def test_combined_conversion_active_highest_signal(self) -> None:
        # Greenfield converted directly into active construction (-60% NDVI and +3.4 dB VV)
        baseline = [self._obs(1, ndvi=0.72, vv=-12.4, vh=-18.5)]
        recent = [self._obs(20, ndvi=0.28, vv=-9.0, vh=-15.8)]

        result = self.engine.evaluate(baseline, recent)
        self.assertEqual(result.severity, AlertSeverity.AMBER)
        self.assertEqual(result.signal_type, "CONVERSION_ACTIVE")
        self.assertGreaterEqual(result.confidence_score, 0.88)

    def test_cloud_cover_low_quality_reduces_confidence(self) -> None:
        baseline = [self._obs(1, ndvi=0.70, vv=-12.0, quality=0.95)]
        clear_recent = [self._obs(20, ndvi=0.30, vv=-9.0, quality=0.95)]
        cloudy_recent = [self._obs(20, ndvi=0.30, vv=-9.0, quality=0.45)]

        clear_res = self.engine.evaluate(baseline, clear_recent)
        cloudy_res = self.engine.evaluate(baseline, cloudy_recent)
        self.assertGreater(clear_res.confidence_score, cloudy_res.confidence_score)

    def test_custom_thresholds_respected(self) -> None:
        strict_engine = AlertEngine(
            thresholds=AlertThresholds(ndvi_drop_pct_threshold=-15.0)
        )
        baseline = [self._obs(1, ndvi=0.60, vv=-11.5)]
        recent = [self._obs(20, ndvi=0.48, vv=-11.4)]  # -20% drop

        self.assertEqual(self.engine.evaluate(baseline, recent).severity, AlertSeverity.GREEN)
        self.assertEqual(strict_engine.evaluate(baseline, recent).severity, AlertSeverity.AMBER)

    def test_evaluate_orm_snapshots_helper(self) -> None:
        site_id = uuid.uuid4()
        snapshots = [
            SatelliteSnapshot(
                site_id=site_id,
                sensor="SENTINEL_2",
                observation_date=date(2026, 4, 1),
                ndvi_mean=0.66,
                sar_vv_db=-11.8,
                valid_pixel_ratio=0.98,
            ),
            SatelliteSnapshot(
                site_id=site_id,
                sensor="SENTINEL_2",
                observation_date=date(2026, 5, 1),
                ndvi_mean=0.64,
                sar_vv_db=-11.7,
                valid_pixel_ratio=0.96,
            ),
            SatelliteSnapshot(
                site_id=site_id,
                sensor="SENTINEL_2",
                observation_date=date(2026, 7, 1),
                ndvi_mean=0.25,
                sar_vv_db=-8.5,
                valid_pixel_ratio=0.94,
            ),
        ]

        alert = self.engine.evaluate_snapshots(site_id=site_id, snapshots=snapshots)
        self.assertEqual(alert.site_id, site_id)
        self.assertEqual(alert.severity, AlertSeverity.AMBER)
        self.assertEqual(alert.signal_type, "CONVERSION_ACTIVE")

    def test_empty_window_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.evaluate([], [self._obs(1)])


if __name__ == "__main__":
    unittest.main()