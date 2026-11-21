from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence
import uuid

from app.models.spatial import AlertSeverity, SatelliteSnapshot, SiteAlert

@dataclass(frozen=True)
class AlertThresholds:
    """
    Limits that trigger an alert when crossed.
    """
    ndvi_drop_pct_threshold: float = -35.0  # e. g. -35% drop in greenery vs past
    sar_vv_spike_db_threshold: float = 2.5  # +2.5 dB radar spike (hard surfaces/buildings)
    sar_vh_spike_db_threshold: float = 2.0  # +2.0 dB radar spike (structures/machinery)
    min_valid_pixel_ratio: float = 0.50 # minimum 50% clear sky (cloud-free)

@dataclass(frozen=True)
class TelemetryObservation:
    """
    Single day of satellite sensor readings
    """
    observation_date: datetime
    ndvi_mean: float | None = None  # Greenery level
    sar_vv_db: float | None = None  # Vertical radar signal
    sar_vh_db: float | None = None  # Cross radar signal
    valid_pixel_ratio: float = 1.0  # Clear sky ratio (1.0 = 100% clear sky)

@dataclass(frozen=True)
class AlertEvaluation:
    """
    Final result after comparing past data with recent data
    """
    severity: AlertSeverity
    signal_type: str
    ndvi_delta_pct: float | None
    sar_vv_delta_db: float | None
    sar_vh_delta_db: float | None
    confidence_score: float
    rationale: str

class AlertEngine:
    def __init__(self, thresholds: AlertThresholds | None = None) -> None:
        self.thresholds = thresholds or AlertThresholds()

    @staticmethod
    def _compute_mean(values: Sequence[float | None]) -> float | None:
        """
        Compute the arithmetic mean of the non-null entries in the provided values.
        Entries whose value is ``None`` are ignored. If no numeric entries remain after
        filtering, the result is ``None`` rather than a numeric average.
        :param values: Values to average, with ``None`` entries excluded from the
            calculation.
        :return: The arithmetic mean of the non-null values, or ``None`` when no
            non-null values are available.
        """
        valid = [v for v in values if v is not None]
        if not valid:
            return None
        return sum(valid) / len(valid)

    def evaluate(self, baseline: Sequence[TelemetryObservation], recent: Sequence[TelemetryObservation]) -> AlertEvaluation:
        """
        Compare baseline and recent telemetry observations to detect meaningful changes in
        vegetation condition and radar backscatter. The evaluation classifies the
        observed signal, assigns alert severity, estimates confidence, and summarizes
        the rationale for the detected condition.
        :param baseline: Historical observations used as the reference telemetry
            window for comparison.
        :param recent: Recent observations used to determine current telemetry
            conditions.
        :raises ValueError: If either observation window is empty.
        :return: Alert evaluation containing severity, signal classification, computed
            deltas, confidence score, and rationale.
        """
        if not baseline or not recent:
            raise ValueError("Both baseline and recent observations are required")

        base_ndvi = self._compute_mean([o.ndvi_mean for o in baseline])
        current_ndvi = self._compute_mean([o.ndvi_mean for o in recent])

        base_vv = self._compute_mean([o.sar_vv_db for o in baseline])
        current_vv = self._compute_mean([o.sar_vv_db for o in recent])

        base_vh = self._compute_mean([o.sar_vh_db for o in baseline])
        current_vh = self._compute_mean([o.sar_vh_db for o in recent])

        # relative NDVI % delta
        ndvi_delta_pct: float | None = None
        if base_ndvi is not None and current_ndvi is not None and abs(base_ndvi) > 0.05:
            ndvi_delta_pct = round(((current_ndvi - base_ndvi) / abs(base_ndvi)) * 100.0, 2)

        # absolute SAR backscatter deltas in decibles (dB)
        sar_vv_delta_db: float | None = None
        if base_vv is not None and current_vv is not None:
            sar_vv_delta_db = round(current_vv - base_vv, 2)

        sar_vh_delta_db: float | None = None
        if base_vh is not None and current_vh is not None:
            sar_vh_delta_db = round(current_vh - base_vh, 2)

        # anomaly triggers
        has_ndvi_drop = (
                ndvi_delta_pct is not None
                and ndvi_delta_pct <= self.thresholds.ndvi_drop_pct_threshold
        )
        has_sar_spike = (
                                sar_vv_delta_db is not None
                                and sar_vv_delta_db >= self.thresholds.sar_vv_spike_db_threshold
                        ) or (
                                sar_vh_delta_db is not None
                                and sar_vh_delta_db >= self.thresholds.sar_vh_spike_db_threshold
                        )

        # classify signal & severity
        if has_ndvi_drop and has_sar_spike:
            severity = AlertSeverity.AMBER
            signal_type = "CONVERSION_ACTIVE"
            rationale = (
                f"Rapid vegetation clearing (NDVI {ndvi_delta_pct:+.1f}%) coupled with "
                f"structural radar backscatter surge (SAR VV {sar_vv_delta_db or 0.0:+.2f} dB)."
            )
        elif has_sar_spike:
            severity = AlertSeverity.AMBER
            signal_type = "STRUCTURAL_EXPANSION"
            rationale = (
                f"Significant SAR double-bounce increase (VV {sar_vv_delta_db or 0.0:+.2f} dB, "
                f"VH {sar_vh_delta_db or 0.0:+.2f} dB) indicating vertical construction or heavy machinery."
            )
        elif has_ndvi_drop:
            severity = AlertSeverity.AMBER
            signal_type = "LAND_CLEARING"
            rationale = (
                f"Sharp optical NDVI decline ({ndvi_delta_pct:+.1f}%) exceeding threshold "
                f"({self.thresholds.ndvi_drop_pct_threshold:.1f}%), indicating earthworks or vegetation removal."
            )
        else:
            severity = AlertSeverity.GREEN
            signal_type = "BASELINE_STABLE"
            rationale = "Optical vegetation index and SAR structural backscatter remain within normal baseline parameters."

        confidence = self._calculate_confidence(
            ndvi_delta_pct=ndvi_delta_pct,
            sar_vv_delta_db=sar_vv_delta_db,
            recent_observations=recent,
            is_amber=(severity == AlertSeverity.AMBER),
        )

        return AlertEvaluation(
            severity=severity,
            signal_type=signal_type,
            ndvi_delta_pct=ndvi_delta_pct,
            sar_vv_delta_db=sar_vv_delta_db,
            sar_vh_delta_db=sar_vh_delta_db,
            confidence_score=confidence,
            rationale=rationale,
        )

    def _calculate_confidence(
            self,
            ndvi_delta_pct: float | None,
            sar_vv_delta_db: float | None,
            recent_observations: Sequence[TelemetryObservation],
            is_amber: bool,
    ) -> float:
        """
        Calculate a normalized confidence score for the current telemetry assessment.
        The score reflects observation quality, anomaly state, and available sensor
        signals. Stable assessments favor data quality and multi-sensor availability,
        while amber assessments increase confidence as NDVI or SAR deviations become
        stronger. The resulting value is rounded and constrained to the expected
        confidence range.
        :param ndvi_delta_pct: Percentage change in NDVI relative to the reference
            baseline, or ``None`` when NDVI data is unavailable.
        :param sar_vv_delta_db: Change in SAR VV backscatter in decibels relative to the
            reference baseline, or ``None`` when SAR data is unavailable.
        :param recent_observations:"""
        avg_quality = self._compute_mean([o.valid_pixel_ratio for o in recent_observations]) or 1.0
        quality_factor = max(0.4, min(1.0, avg_quality))

        if not is_amber:
            # Stable baseline confidence reflects data quality and multi-sensor availability
            sensor_bonus = 0.1 if (ndvi_delta_pct is not None and sar_vv_delta_db is not None) else 0.0
            return round(min(0.98, 0.75 * quality_factor + sensor_bonus), 2)

        # Magnitude score scales with how far beyond threshold the anomaly pushes
        ndvi_strength = 0.0
        if ndvi_delta_pct is not None and ndvi_delta_pct < 0:
            ndvi_strength = min(1.0, abs(ndvi_delta_pct) / 70.0)

        sar_strength = 0.0
        if sar_vv_delta_db is not None and sar_vv_delta_db > 0:
            sar_strength = min(1.0, sar_vv_delta_db / 5.0)

        combined_strength = max(ndvi_strength, sar_strength)
        if ndvi_strength > 0.5 and sar_strength > 0.5:
            # Multi-sensor confirmation boosts confidence
            combined_strength = min(1.0, (ndvi_strength + sar_strength) * 0.65)

        raw_confidence = (0.55 + 0.45 * combined_strength) * quality_factor
        return round(max(0.50, min(0.99, raw_confidence)), 2)

    def evaluate_snapshots(
            self,
            site_id: uuid.UUID,
            snapshots: Sequence[SatelliteSnapshot],
            split_ratio: float = 0.7,
    ) -> SiteAlert:
        """
        Evaluate satellite snapshots for a site and produce an alert describing
        detected vegetation and radar signal changes. The snapshots are ordered by
        observation date, divided into baseline and recent observation windows, and
        converted into telemetry observations before the site-level alert is built
        from the evaluation result.
        :param site_id: Identifier of the site being evaluated.
        :param snapshots: Satellite snapshots used to build the chronological
            telemetry series.
        :param split_ratio: Fraction of ordered snapshots assigned to the baseline
            window before recent observations are evaluated.
        :raises ValueError: If fewer than two snapshots are provided.
        :return: Site alert containing severity, signal type, change metrics, and
            confidence score for the evaluated site.
        """
        ordered = sorted(snapshots, key=lambda s: s.observation_date)
        if len(ordered) < 2:
            raise ValueError("At least 2 chronological snapshots are required to evaluate a site.")

        split_idx = max(1, min(len(ordered) - 1, int(len(ordered) * split_ratio)))
        observations = [
            TelemetryObservation(
                observation_date=datetime.combine(s.observation_date, datetime.min.time(), tzinfo=timezone.utc),
                ndvi_mean=s.ndvi_mean,
                sar_vv_db=s.sar_vv_db,
                sar_vh_db=s.sar_vh_db,
                valid_pixel_ratio=s.valid_pixel_ratio if s.valid_pixel_ratio is not None else 1.0,
            )
            for s in ordered
        ]

        evaluation = self.evaluate(
            baseline=observations[:split_idx],
            recent=observations[split_idx:],
        )

        return SiteAlert(
            site_id=site_id,
            severity=evaluation.severity,
            signal_type=evaluation.signal_type,
            ndvi_delta_pct=evaluation.ndvi_delta_pct,
            sar_vv_delta_db=evaluation.sar_vv_delta_db,
            confidence_score=evaluation.confidence_score,
        )

def evaluate_site_anomalies(
        site_id: uuid.UUID,
        snapshots: Sequence[SatelliteSnapshot],
        split_ratio: float = 0.7,
) -> SiteAlert:
    """Convenience wrapper around AlertEngine.evaluate_snapshots."""
    return AlertEngine().evaluate_snapshots(
        site_id=site_id,
        snapshots=snapshots,
        split_ratio=split_ratio,
)