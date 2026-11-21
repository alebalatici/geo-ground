import unittest
from unittest.mock import MagicMock, patch

from app.integrations.llm.client import GeminiClient
from app.integrations.llm.prompts import build_assistant_prompt, build_executive_prompt
from app.schemas.intelligence import ChatTurn, TelemetryContextPayload


class TestGeminiIntegration(unittest.TestCase):
    """
    Tests covering prompt grounding, Gemini invocation, and deterministic fallback.
    """
    def setUp(self) -> None:
        self.sample_telemetry = TelemetryContextPayload(
            site_id="11111111-1111-1111-1111-111111111111",
            site_name="Cluj Innovation Logistics Hub",
            city="Cluj-Napoca",
            area_hectares=14.5,
            signal_type="CONVERSION_ACTIVE",
            severity="AMBER",
            confidence_score=0.92,
            ndvi_baseline=0.68,
            ndvi_current=0.24,
            ndvi_delta=-0.44,
            sar_vv_delta_db=3.4,
            sar_vh_delta_db=2.1,
            lst_current_c=31.2,
            lst_delta_c=2.8,
            observation_window="2026-08-01 to 2026-10-15",
        )

    def test_prompts_include_exact_telemetry_metrics(self) -> None:
        """
        Test for exact match of telemetry metrics in prompt.
        """
        exec_prompt = build_executive_prompt(self.sample_telemetry)
        self.assertIn("Cluj Innovation Logistics Hub", exec_prompt)
        self.assertIn("CONVERSION_ACTIVE", exec_prompt)
        self.assertIn("-0.44", exec_prompt)
        self.assertIn("+3.40 dB", exec_prompt)

        chat_prompt = build_assistant_prompt(
            self.sample_telemetry,
            user_message="When did vegetation clearing start?",
            active_year=2025,
        )
        self.assertIn("Timeline Slider Active Year Focus: 2025", chat_prompt)
        self.assertIn("When did vegetation clearing start?", chat_prompt)

    @patch("app.integrations.llm.client.genai.Client")
    def test_gemini_executive_summary_success(self, mock_genai_cls: MagicMock) -> None:
        """
        Test that the Gemini client returns a successful response.
        """
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.models.generate_content.return_value = MagicMock(
            text="Active land clearing and early vertical construction detected."
        )
        mock_genai_cls.return_value = mock_gemini_instance

        client = GeminiClient(api_key="fake-gemini-key", model="gemini-2.5-flash")
        result = client.generate_executive_summary(self.sample_telemetry)

        self.assertEqual(
            result.text, "Active land clearing and early vertical construction detected."
        )
        self.assertEqual(result.provider, "gemini:gemini-2.5-flash")

    @patch("app.integrations.llm.client.genai.Client")
    def test_gemini_chat_with_history_success(self, mock_genai_cls: MagicMock) -> None:
        """
        Test that the Gemini client returns a successful response with history.
        """
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.models.generate_content.return_value = MagicMock(
            text="SAR VV spiked by +3.40 dB, confirming structural foundations."
        )
        mock_genai_cls.return_value = mock_gemini_instance

        client = GeminiClient(api_key="fake-gemini-key", model="gemini-2.5-flash")
        result = client.generate_chat_reply(
            telemetry=self.sample_telemetry,
            user_message="What does the radar spike mean?",
            history=[
                ChatTurn(role="user", content="Hi"),
                ChatTurn(role="assistant", content="Hello, ask me about this parcel."),
            ],
            active_year=2026,
        )

        self.assertEqual(result.provider, "gemini:gemini-2.5-flash")
        self.assertIn("+3.40 dB", result.text)
        call_kwargs = mock_gemini_instance.models.generate_content.call_args.kwargs
        self.assertEqual(len(call_kwargs["contents"]), 3)

    @patch("app.integrations.llm.client.genai.Client")
    def test_fallback_when_gemini_raises_exception(self, mock_genai_cls: MagicMock) -> None:
        """
        Test that the Gemini client returns a fallback response when an exception is raised.
        """
        mock_gemini_instance = MagicMock()
        mock_gemini_instance.models.generate_content.side_effect = RuntimeError(
            "429 Quota Exceeded"
        )
        mock_genai_cls.return_value = mock_gemini_instance

        client = GeminiClient(api_key="fake-gemini-key")
        result = client.generate_executive_summary(self.sample_telemetry)

        self.assertEqual(result.provider, "deterministic_fallback")
        self.assertIn("Cluj Innovation Logistics Hub", result.text)
        self.assertIn("CONVERSION_ACTIVE", result.text)

    def test_fallback_when_api_key_missing(self) -> None:
        """
        Test that the deterministic fallback is used when the API key is missing.
        """
        client = GeminiClient(api_key=None)
        result = client.generate_chat_reply(
            telemetry=self.sample_telemetry,
            user_message="Give me a status check.",
        )

        self.assertEqual(result.provider, "deterministic_fallback")
        self.assertIn("-0.44", result.text)


if __name__ == "__main__":
    unittest.main()