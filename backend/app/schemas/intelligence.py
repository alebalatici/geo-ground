from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

"""
Pydantic v2 schemas for the GeoGround Gemini Executive & Assistant layer.
"""
class TelemetryContextPayload(BaseModel):
    """
    Structured mathematical telemetry extracted from PostGIS & AlertEngine.
    """
    site_id: str
    site_name: str
    city: str
    area_hectares: float | None = None
    signal_type: str = "BASELINE_STABLE"
    severity: str = "GREEN"
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ndvi_baseline: float | None = None
    ndvi_current: float | None = None
    ndvi_delta: float | None = None
    sar_vv_delta_db: float | None = None
    sar_vh_delta_db: float | None = None
    lst_current_c: float | None = None
    lst_delta_c: float | None = None
    observation_window: str | None = None
    historical_trend_notes: str | None = None


class ExecutiveSummaryResponse(BaseModel):
    """
    Represents an generated executive summary for site-level signal analysis.
    Stores the identifying site information, analyzed signal context, severity
    classification, generated narrative summary, supporting signal highlights, the
    provider responsible for generation, and the timestamp at which the response was
    produced.
    :ivar site_id: Unique identifier of the site associated with the summary.
    :ivar site_name: Human-readable name of the site associated with the summary.
    :ivar signal_type: Category or type of signal summarized in the response.
    :ivar severity: Severity level assigned to the summarized signal context.
    :ivar summary: Generated executive summary text.
    :ivar key_signals: Important signal details or highlights supporting the
        summary.
    :ivar provider_used: Name or identifier of the provider used to generate the
        summary.
    :ivar generated_at: Timestamp indicating when the summary was generated.
    """
    site_id: str
    site_name: str
    signal_type: str
    severity: str
    summary: str
    key_signals: list[str] = Field(default_factory=list)
    provider_used: str
    generated_at: datetime


class ChatTurn(BaseModel):
    """
    Single conversational turn in the persistent AI sidebar.
    User messages are "user" and assistant responses are "assistant".
    """
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class SiteChatRequest(BaseModel):
    """
    User query submitted from the persistent sidebar assistant.
    """
    message: str = Field(..., min_length=1, max_length=2000)
    active_year: int | None = Field(
        default=None,
        ge=2000,
        le=2030,
        description="Currently selected year on the 2000-present Timeline Slider.",
    )
    history: list[ChatTurn] = Field(
        default_factory=list,
        max_length=10,
        description="Recent conversation turns for contextual continuity.",
    )


class SiteChatResponse(BaseModel):
    """
    Grounded assistant response tied strictly to active site telemetry.
    """
    site_id: str
    reply: str
    referenced_metrics: dict[str, float | str | None] = Field(default_factory=dict)
    provider_used: str