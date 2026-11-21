"""
Google Gemini client (google-genai SDK) with a deterministic offline safety net.
The Gemini client is configured from application settings.
"""

from dataclasses import dataclass
from functools import lru_cache
import logging
from typing import Sequence

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.integrations.llm.prompts import (
    SYSTEM_PROMPT_ASSISTANT,
    SYSTEM_PROMPT_EXECUTIVE,
    build_assistant_prompt,
    build_executive_prompt,
)

from app.schemas.intelligence import ChatTurn, TelemetryContextPayload

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMGenerationResult:
    """Represents the immutable result of a language model generation.
    Stores the generated text together with the name or identifier of the provider
    that produced it. The instance is frozen after creation, making it suitable for
    passing generation output through application layers without accidental mutation.
    """
    text: str
    provider: str


class GeminiClient:
    """
    Gateway wrapping Google Gemini via the official google-genai SDK.
    """
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        timeout_seconds: float = 15.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

        self._client = (
            genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=int(self.timeout_seconds * 1000)),
            )
            if self.api_key
            else None
        )

    def generate_executive_summary(
        self, telemetry: TelemetryContextPayload
    ) -> LLMGenerationResult:
        """
        Generate an executive intelligence brief from site telemetry.
        :param telemetry: Telemetry context containing site metadata, signal status,
        """
        user_prompt = build_executive_prompt(telemetry)
        text = self._call_gemini(
            system_prompt=SYSTEM_PROMPT_EXECUTIVE,
            user_prompt=user_prompt,
            history=None,
        )
        if text:
            return LLMGenerationResult(text=text, provider=f"gemini:{self.model}")

        return LLMGenerationResult(
            text=self._deterministic_executive_fallback(telemetry),
            provider="deterministic_fallback",
        )

    def generate_chat_reply(
        self,
        telemetry: TelemetryContextPayload,
        user_message: str,
        history: Sequence[ChatTurn] | None = None,
        active_year: int | None = None,
    ) -> LLMGenerationResult:
        """
        Answer a contextual question about the active site.
        :param telemetry: Telemetry context containing site metadata, classification
        """
        user_prompt = build_assistant_prompt(
            telemetry=telemetry,
            user_message=user_message,
            active_year=active_year,
        )
        text = self._call_gemini(
            system_prompt=SYSTEM_PROMPT_ASSISTANT,
            user_prompt=user_prompt,
            history=history,
        )
        if text:
            return LLMGenerationResult(text=text, provider=f"gemini:{self.model}")

        return LLMGenerationResult(
            text=self._deterministic_chat_fallback(telemetry),
            provider="deterministic_fallback",
        )

    def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Sequence[ChatTurn] | None = None,
    ) -> str | None:
        """
        Invoke Google Gemini; return None if unconfigured or on API failure.
        :param system_prompt: System prompt to guide the model's responses.
        """
        if self._client is None:
            logger.warning("GEMINI_API_KEY is not configured; using deterministic fallback.")
            return None

        contents: list[types.Content] = []
        if history:
            for turn in history:
                gemini_role = "user" if turn.role == "user" else "model"
                contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[types.Part.from_text(text=turn.content)],
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_prompt)],
            )
        )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                    max_output_tokens=600,
                ),
            )
            return (response.text or "").strip() or None
        except Exception as exc:
            logger.warning("Gemini API call failed: %s", exc)
            return None

    @staticmethod
    def _deterministic_executive_fallback(telemetry: TelemetryContextPayload) -> str:
        """
        Provides a deterministic fallback path for executive telemetry reporting when
        generated narrative content is unavailable. The text is assembled from the
        available site, signal, confidence, optical, and radar telemetry fields while
        preserving stable formatting for downstream presentation.
        :param telemetry: Telemetry context containing the site identity, location,
            signal status, severity, confidence score, and optional optical and SAR
            delta measurements used to compose the fallback narrative.
        :return: Executive-ready fallback narrative describing the current site status,
            supporting multi-sensor telemetry, and recommended monitoring action.
        """
        ndvi_str = f"{telemetry.ndvi_delta:+.2f}" if telemetry.ndvi_delta is not None else "N/A"
        vv_str = (
            f"{telemetry.sar_vv_delta_db:+.2f} dB"
            if telemetry.sar_vv_delta_db is not None
            else "N/A"
        )
        conf_pct = f"{telemetry.confidence_score * 100:.0f}%"

        return (
            f"Site {telemetry.site_name} ({telemetry.city}) currently registers a "
            f"{telemetry.signal_type} status ({telemetry.severity} severity, {conf_pct} confidence). "
            f"Multi-sensor telemetry shows an optical NDVI shift of {ndvi_str} alongside a "
            f"Sentinel-1 SAR VV backscatter delta of {vv_str}.\n\n"
            f"Recommended action: Continue automated 10m multi-spectral monitoring and cross-check "
            f"observed physical ground changes against local municipal urbanism certificates."
        )

    @staticmethod
    def _deterministic_chat_fallback(telemetry: TelemetryContextPayload) -> str:
        """
        Provides a deterministic fallback synthesis for satellite telemetry when AI
        synthesis is unavailable. The generated narrative emphasizes the current
        classification, severity, vegetation and radar deltas, confidence, and the
        temporary unavailability of AI-generated analysis.
        :param telemetry: Telemetry context containing site metadata, classification
            details, severity, confidence, and available sensor delta metrics.
        :return: Human-readable fallback telemetry summary.
        """
        ndvi_str = f"{telemetry.ndvi_delta:+.2f}" if telemetry.ndvi_delta is not None else "N/A"
        vv_str = (
            f"{telemetry.sar_vv_delta_db:+.2f} dB"
            if telemetry.sar_vv_delta_db is not None
            else "N/A"
        )
        return (
            f"Based on recorded satellite telemetry for {telemetry.site_name} ({telemetry.city}): "
            f"current classification is {telemetry.signal_type} ({telemetry.severity}), "
            f"with NDVI delta {ndvi_str} and SAR VV delta {vv_str} "
            f"(confidence {telemetry.confidence_score * 100:.0f}%). "
            f"AI synthesis is temporarily unavailable, so verified sensor metrics are displayed."
        )

@lru_cache(maxsize=1)
def get_llm_client() -> GeminiClient:
    """
    Create and cache the configured Gemini language model client.
    Initializes a Gemini client using the application settings for the API key,
    model name, and request timeout. The result is cached by the surrounding LRU
    cache configuration, so repeated calls return the same client instance until the
    cache is cleared or the process ends.
    :return: Configured Gemini client instance ready for language model requests.
    """
    settings = get_settings()
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.LLM_MODEL_GEMINI,
        timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
    )