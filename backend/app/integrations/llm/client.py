"""
Multi-provider LLM Gateway (Groq primary + Google Gemini backup) with a deterministic
offline safety net.
"""

from dataclasses import dataclass
from functools import lru_cache
import logging
from typing import Sequence

from google import genai
from google.genai import types
from groq import Groq

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
    """Represents the immutable result of a language model generation."""

    text: str
    provider: str


class GeminiClient:
    """
    Gateway orchestrating Groq (primary low-latency inference) and Google Gemini
    (secondary fallback) with deterministic offline protection.
    """

    GEMINI_FALLBACK_MODELS: tuple[str, ...] = ("gemini-3.5-flash-lite", "gemini-3.8-flash")

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-3.8-flash",
        timeout_seconds: float = 15.0,
        groq_api_key: str | None = None,
        groq_model: str = "llama-3.3-70b-versatile",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

        self.groq_api_key = groq_api_key
        self.groq_model = groq_model

        self._groq_client = (
            Groq(api_key=self.groq_api_key, timeout=min(self.timeout_seconds, 8.0))
            if self.groq_api_key
            else None
        )

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
        """Generate an executive intelligence brief from site telemetry."""
        user_prompt = build_executive_prompt(telemetry)
        text, provider_label = self._generate(
            system_prompt=SYSTEM_PROMPT_EXECUTIVE,
            user_prompt=user_prompt,
            history=None,
        )
        if text and provider_label:
            return LLMGenerationResult(text=text, provider=provider_label)

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
        """Answer a contextual question about the active site."""
        user_prompt = build_assistant_prompt(
            telemetry=telemetry,
            user_message=user_message,
            active_year=active_year,
        )
        text, provider_label = self._generate(
            system_prompt=SYSTEM_PROMPT_ASSISTANT,
            user_prompt=user_prompt,
            history=history,
        )
        if text and provider_label:
            return LLMGenerationResult(text=text, provider=provider_label)

        return LLMGenerationResult(
            text=self._deterministic_chat_fallback(telemetry),
            provider="deterministic_fallback",
        )

    def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Sequence[ChatTurn] | None = None,
    ) -> tuple[str | None, str | None]:
        """Try Groq first for instant responses, then fall back to Gemini."""
        groq_text = self._call_groq(system_prompt, user_prompt, history)
        if groq_text:
            return groq_text, f"groq:{self.groq_model}"

        gemini_text, used_model = self._call_gemini(system_prompt, user_prompt, history)
        if gemini_text and used_model:
            return gemini_text, f"gemini:{used_model}"

        return None, None

    def _call_groq(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Sequence[ChatTurn] | None = None,
    ) -> str | None:
        """Invoke Groq API (OpenAI-compatible messages format)."""
        if self._groq_client is None:
            return None

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            for turn in history:
                role = "user" if turn.role == "user" else "assistant"
                messages.append({"role": role, "content": turn.content})
        messages.append({"role": "user", "content": user_prompt})

        try:
            completion = self._groq_client.chat.completions.create(
                model=self.groq_model,
                messages=messages,
                temperature=0.25,
                max_tokens=500,
            )
            content = completion.choices[0].message.content if completion.choices else None
            return (content or "").strip() or None
        except Exception as exc:
            logger.warning("Groq API call failed on %s: %s", self.groq_model, exc)
            return None

    def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Sequence[ChatTurn] | None = None,
    ) -> tuple[str | None, str | None]:
        """Invoke Google Gemini as backup provider."""
        if self._client is None:
            return None, None

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

        candidate_models = list(dict.fromkeys([self.model, *self.GEMINI_FALLBACK_MODELS]))

        for model_name in candidate_models:
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.25,
                        max_output_tokens=500,
                    ),
                )
                text = (response.text or "").strip()
                if text:
                    return text, model_name
            except Exception as exc:
                logger.warning("Gemini API call failed on %s: %s", model_name, exc)
                continue

        return None, None

    @staticmethod
    def _deterministic_executive_fallback(telemetry: TelemetryContextPayload) -> str:
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
    """Create and cache the configured multi-provider LLM client."""
    settings = get_settings()
    return GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.LLM_MODEL_GEMINI,
        timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
        groq_api_key=settings.GROQ_API_KEY,
        groq_model=settings.LLM_MODEL_GROQ,
    )