from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.integrations.llm.client import GeminiClient, get_llm_client
from app.repositories.site_repository import SiteRepository
from app.schemas.intelligence import (
    ExecutiveSummaryResponse,
    SiteChatRequest,
    SiteChatResponse,
    TelemetryContextPayload,
)

class SiteNotFoundError(Exception):
    """
    Raised when the requested monitored parcel does not exist in PostGIS.
    """

class IntelligenceService:
    """
    Coordinate intelligence generation for monitored site telemetry.
    Provides a service layer that gathers site, alert, and satellite snapshot data from
    the configured repository, prepares telemetry context, and delegates natural
    language generation to the configured language model client. The service returns
    structured response objects for executive summaries and contextual site chat
    answers.
    :ivar db: Database session used for repository operations.
    :type db: Session
    :ivar site_repo: Repository used to retrieve monitored site records, alerts, and
        snapshots.
    :type site_repo: SiteRepository
    :ivar llm_client: Client used to generate natural language intelligence from
        telemetry context.
    :type llm_client: GeminiClient
    """
    def __init__(
        self,
        db: Session,
        site_repository: SiteRepository | None = None,
        llm_client: GeminiClient | None = None,
    ) -> None:
        self.db = db
        self.site_repo = site_repository or SiteRepository()
        self.llm_client = llm_client or get_llm_client()

    def get_site_executive_summary(
        self, site_id: UUID | str
    ) -> ExecutiveSummaryResponse:
        """
        Generate an executive summary for the specified site.
        Loads the site's telemetry, creates a concise executive summary from the
        available signals, derives key signal badges, and packages the generated
        content with the relevant site and provider metadata.
        :param site_id: Identifier of the site for which the executive summary is
            generated.
        :return: Generated executive summary details, including site identity,
            signal information, summary content, key signals, provider metadata, and
            the generation timestamp.
        """
        telemetry = self._load_site_telemetry(site_id)
        result = self.llm_client.generate_executive_summary(telemetry)

        key_signals = self._derive_key_signal_badges(telemetry)

        return ExecutiveSummaryResponse(
            site_id=telemetry.site_id,
            site_name=telemetry.site_name,
            signal_type=telemetry.signal_type,
            severity=telemetry.severity,
            summary=result.text,
            key_signals=key_signals,
            provider_used=result.provider,
            generated_at=datetime.now(timezone.utc),
        )

    def answer_site_chat(
        self, site_id: UUID | str, request: SiteChatRequest
    ) -> SiteChatResponse:
        """
        Build a chat response for a monitored site by combining telemetry context,
        conversation history, and language-model output. The response includes the
        generated reply, the metrics referenced for contextual grounding, and the
        provider selected for generation.
        :param site_id: Identifier of the site for which the chat reply is generated.
        :param request: Chat request containing the user message, conversation history,
            and active analysis year.
        :return: Chat response containing the generated reply, referenced telemetry
            metrics, site identifier, and provider information.
        """
        telemetry = self._load_site_telemetry(site_id, active_year=request.active_year)
        result = self.llm_client.generate_chat_reply(
            telemetry=telemetry,
            user_message=request.message,
            history=request.history,
            active_year=request.active_year,
        )

        return SiteChatResponse(
            site_id=telemetry.site_id,
            reply=result.text,
            referenced_metrics={
                "signal_type": telemetry.signal_type,
                "severity": telemetry.severity,
                "ndvi_delta": telemetry.ndvi_delta,
                "sar_vv_delta_db": telemetry.sar_vv_delta_db,
                "lst_current_c": telemetry.lst_current_c,
                "confidence_score": telemetry.confidence_score,
            },
            provider_used=result.provider,
        )

    def _load_site_telemetry(
        self, site_id: UUID | str, active_year: int | None = None
    ) -> TelemetryContextPayload:
        """
        Load monitored-site telemetry from persisted site, alert, and snapshot data.
        Assembles the current monitoring context by combining site metadata, the latest
        alert signal, normalized numeric measurements, and historical snapshot notes.
        When no alert is available, baseline-stable signal values are used.
        :param site_id: Identifier of the monitored site whose telemetry context should
            be loaded.
        :param active_year: Optional year used to focus historical snapshot
            summarization.
        :raises SiteNotFoundError: If no monitored site exists for the supplied
            identifier.
        :return: Telemetry context payload containing site metadata, alert-derived
            measurements, and historical trend notes.
        """
        site = self.site_repo.get_site_by_id(self.db, site_id)
        if site is None:
            raise SiteNotFoundError(f"Monitored site '{site_id}' was not found.")

        latest_alert = self.site_repo.get_latest_alert(self.db, site_id)
        snapshots = self.site_repo.get_snapshots_for_site(self.db, site_id)

        historical_notes = self._summarize_historical_snapshots(
            snapshots=snapshots, active_year=active_year
        )

        return TelemetryContextPayload(
            site_id=str(getattr(site, "id", site_id)),
            site_name=getattr(site, "name", "Unnamed Parcel"),
            city=getattr(site, "city", "Romania"),
            area_hectares=self._safe_float(getattr(site, "area_hectares", None)),
            signal_type=getattr(latest_alert, "signal_type", "BASELINE_STABLE")
            if latest_alert
            else "BASELINE_STABLE",
            severity=getattr(latest_alert, "severity", "GREEN")
            if latest_alert
            else "GREEN",
            confidence_score=self._safe_float(
                getattr(latest_alert, "confidence_score", 0.0)
            )
            or 0.0,
            ndvi_baseline=self._safe_float(getattr(latest_alert, "ndvi_baseline", None)),
            ndvi_current=self._safe_float(getattr(latest_alert, "ndvi_current", None)),
            ndvi_delta=self._safe_float(getattr(latest_alert, "ndvi_delta", None)),

            sar_vv_delta_db=self._safe_float(
                getattr(latest_alert, "sar_vv_delta_db", None)
                or getattr(latest_alert, "vv_delta_db", None)
            ),

            sar_vh_delta_db=self._safe_float(
                getattr(latest_alert, "sar_vh_delta_db", None)
                or getattr(latest_alert, "vh_delta_db", None)
            ),
            lst_current_c=self._safe_float(getattr(latest_alert, "lst_current_c", None)),
            lst_delta_c=self._safe_float(getattr(latest_alert, "lst_delta_c", None)),
            observation_window=getattr(latest_alert, "observation_window", None),
            historical_trend_notes=historical_notes,
        )

    @staticmethod
    def _summarize_historical_snapshots(
        snapshots: list[Any], active_year: int | None = None
    ) -> str | None:
        """
        Builds a concise textual overview of archived satellite observation records.
        The summary aggregates the available observation history into a short
        human-readable narrative suitable for reports or diagnostics. It counts archived
        records, determines the observed calendar-year span when dates are available,
        and can include selected year-focused observation details. Missing optional
        measurement fields are preserved as absent values rather than normalized or
        estimated.
        :param snapshots: Collection of snapshot-like objects to inspect.
        :param active_year: Calendar year to highlight when matching records are
            present.
        :return: Human-readable archive summary, or ``None`` when no snapshots are
            provided.
        """
        if not snapshots:
            return None

        year_focus_records = []
        all_years: list[int] = []

        for snap in snapshots:
            obs_date = getattr(snap, "observation_date", None) or getattr(snap, "date", None)
            year = getattr(obs_date, "year", None)
            if isinstance(year, int):
                all_years.append(year)
                if active_year is not None and year == active_year:
                    sensor = getattr(snap, "sensor", "UNKNOWN")
                    ndvi = getattr(snap, "ndvi_mean", None) or getattr(snap, "ndvi", None)
                    vv = getattr(snap, "vv_mean", None) or getattr(snap, "sar_vv", None)
                    lst = getattr(snap, "lst_c", None)
                    year_focus_records.append(
                        f"{obs_date} [{sensor}]: NDVI={ndvi}, VV={vv} dB, LST={lst} °C"
                    )

        parts: list[str] = [f"Total archived satellite observations: {len(snapshots)}."]
        if all_years:
            parts.append(f"Archive span: {min(all_years)}–{max(all_years)}.")
        if active_year is not None:
            if year_focus_records:
                sample = "; ".join(year_focus_records[:4])
                parts.append(f"Observations in {active_year}: {sample}")
            else:
                parts.append(f"No archived snapshots recorded specifically for {active_year}.")

        return " ".join(parts)

    @staticmethod
    def _derive_key_signal_badges(telemetry: TelemetryContextPayload) -> list[str]:
        """
        Extract concise metric pills for the Executive View UI.
        """
        badges: list[str] = []
        if telemetry.ndvi_delta is not None:
            badges.append(f"NDVI {telemetry.ndvi_delta:+.2f}")
        if telemetry.sar_vv_delta_db is not None:
            badges.append(f"SAR VV {telemetry.sar_vv_delta_db:+.2f} dB")
        if telemetry.lst_delta_c is not None:
            badges.append(f"LST {telemetry.lst_delta_c:+.1f} °C")
        badges.append(f"Confidence {telemetry.confidence_score * 100:.0f}%")
        return badges

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None