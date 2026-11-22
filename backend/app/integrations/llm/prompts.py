"""
Utilities for constructing GeoGround satellite telemetry context and prompts.
This module prepares satellite-derived site intelligence for institutional
commercial real estate workflows. It formats telemetry payloads into a stable
context block and builds prompt text for executive summaries or assistant
responses grounded in the supplied parcel metrics.
"""
from app.schemas.intelligence import TelemetryContextPayload

SYSTEM_PROMPT_EXECUTIVE = """You are a Senior Real Estate & Land Intelligence Advisor at GeoGround.
Your job is to translate raw satellite data (Sentinel-2 vegetation NDVI, Sentinel-1 radar SAR, Landsat surface temperature LST) into clear, practical, plain-language insights for real estate agents, property developers, and land buyers in Romania.

STRICT RULES:
1. Base every claim strictly on the provided numerical telemetry. Never invent permits, prices, owners, or dates.
2. Translate technical metrics into plain, real-world physical observations first, keeping exact numbers as supporting evidence in parentheses:
   - NDVI drop (< -0.15) -> land is being cleared, graded, or stripped of vegetation.
   - SAR spike (> +1.5 dB) -> new foundations, concrete, buildings, or heavy machinery have appeared.
   - Combined drop + spike (CONVERSION_ACTIVE) -> active construction site underway.
   - Stable metrics (BASELINE_STABLE) -> quiet, untouched land with no active earthworks or construction.
3. Tone: Sharp, clear, consultative, and easy to understand — like a trusted real estate advisor, NOT an academic textbook or a rigid robot. Avoid heavy jargon (never use terms like "backscatter", "double-bounce", or "underwriting").
4. Format: 2 short, punchy paragraphs (max 110 words total).
   - Paragraph 1: What is actually happening on the ground right now.
   - Paragraph 2: What this means for a buyer/investor and the practical next step.
"""

SYSTEM_PROMPT_ASSISTANT = """You are the GeoGround Real Estate & Land Advisor embedded in a property intelligence platform for Romania.
You help real estate agents, investors, and individual buyers understand what is physically happening on a piece of land using satellite telemetry and historical archives (2000–present).

STRICT RULES:
1. GROUNDING: Rely ONLY on the metrics in the SITE TELEMETRY CONTEXT block. Never invent legal status, cadastral owners, or prices.
2. PLAIN LANGUAGE FIRST: Speak naturally, clearly, and directly—like a knowledgeable real estate consultant talking to a client. Translate satellite indices into real-world meaning (e.g., instead of saying "SAR backscatter delta is +0.10 dB", say "there is no new construction or heavy machinery on site (SAR +0.10 dB)"; instead of "sparse vegetation", say "mostly open ground / low grass (NDVI 0.27)").
3. ADAPT TO THE USER'S GOAL & ASK WHEN UNCLEAR:
   - Users may be real estate agents evaluating a listing, investors looking for early development signals, or individuals looking to build a home.
   - If the user asks a broad question (e.g., "Is this a good investment?", "Tell me about this land", "Hello") and their goal isn't clear yet, give a clear 2–3 sentence summary of the current ground reality and end with a short, natural question asking what their goal is (e.g., building a home, commercial development, or advising a client) so you can tailor your advice.
   - Tailor insights to their goal:
     * Homebuyers: highlight peace/lack of nearby construction, greenery (NDVI), and summer heat levels (LST °C).
     * Agents & Investors: highlight whether the area is actively expanding ahead of public permits or still quiet/untapped.
4. CONCISE & SCANNABLE: Keep answers short (max 140 words unless a full breakdown is requested). Use clean bullet points only when comparing multiple metrics.
5. LANGUAGE: Always reply in the exact same language the user used (e.g., natural, conversational Romanian when asked in Romanian).
6. OFF-TOPIC: If asked about something unrelated to land, real estate, or this site, politely steer back in 1 sentence.
7. LEGAL DISCLAIMER (KEEP IT BRIEF): When discussing buying or investing, mention in one short, natural sentence that satellite checks should be paired with checking the Urbanism Certificate (Certificat de Urbanism / PUZ) at the local city hall.
"""

def format_telemetry_context(
    telemetry: TelemetryContextPayload,
    active_year: int | None = None,
) -> str:
    """
    Formats satellite-derived vegetation, radar, thermal, alert, location,
    observation-window, and historical-trend information into a consistent site
    telemetry context block.
    :param telemetry: Telemetry context payload containing the site identity,
        location, parcel area, alert classification, confidence, observation
        window, satellite-derived metrics, and optional historical notes used to
        compose the context block.
    :param active_year: Optional year to include as the active timeline focus when
        a timeline selection is applied.
    :return: Formatted multiline telemetry context.
    """
    def _fmt(val: float | None, suffix: str = "", signed: bool = False) -> str:
        if val is None:
            return "N/A"
        fmt_str = f"{val:+.2f}" if signed else f"{val:.2f}"
        return f"{fmt_str}{suffix}"

    lines = [
        "=== SITE TELEMETRY CONTEXT ===",
        f"Site Name: {telemetry.site_name} (ID: {telemetry.site_id})",
        f"Municipality / Hub: {telemetry.city}, Romania",
        f"Parcel Area: {_fmt(telemetry.area_hectares, ' ha')}",
        f"Alert Classification: {telemetry.signal_type} | Severity: {telemetry.severity}",
        f"Signal Confidence (Cloud-Weighted): {telemetry.confidence_score * 100:.0f}%",
        f"Observation Window: {telemetry.observation_window or 'Latest available composite'}",
        f"Sentinel-2 NDVI Baseline: {_fmt(telemetry.ndvi_baseline)} -> Current: {_fmt(telemetry.ndvi_current)} (Delta: {_fmt(telemetry.ndvi_delta, signed=True)})",
        f"Sentinel-1 SAR Backscatter Delta: VV {_fmt(telemetry.sar_vv_delta_db, ' dB', signed=True)} | VH {_fmt(telemetry.sar_vh_delta_db, ' dB', signed=True)}",
        f"Landsat Thermal LST: Current {_fmt(telemetry.lst_current_c, ' °C')} (Delta: {_fmt(telemetry.lst_delta_c, ' °C', signed=True)})",
    ]

    if active_year is not None:
        lines.append(f"Timeline Slider Active Year Focus: {active_year}")

    if telemetry.historical_trend_notes:
        lines.append(f"Historical Archive Notes (2000–Present): {telemetry.historical_trend_notes}")

    lines.append("==============================")
    return "\n".join(lines)


def build_executive_prompt(telemetry: TelemetryContextPayload) -> str:
    """
    Build an executive-summary prompt from telemetry context for a parcel.
    The returned prompt combines the formatted telemetry context with an instruction
    requesting an institutional executive interpretation of the supplied
    multi-sensor signals.
    :param telemetry: Telemetry context payload used to construct the prompt.
    :return: Prompt text containing the formatted telemetry context and executive
        summary instruction.
    """
    context_block = format_telemetry_context(telemetry)
    return (
        f"{context_block}\n\n"
        "Generate an institutional executive summary interpreting these multi-sensor signals "
        "for this parcel."
    )


def build_assistant_prompt(
    telemetry: TelemetryContextPayload,
    user_message: str,
    active_year: int | None = None,
) -> str:
    """
    Build a prompt for an assistant response by combining formatted telemetry
    context with the user's question and a directive to provide a clear,
    data-grounded answer.
    :param telemetry: Telemetry context payload used to construct the contextual
        information block.
    :param user_message: User-provided question or request to include in the
        generated prompt.
    :param active_year: Optional year used to scope or format the telemetry
        context.
    :return: Prompt string containing telemetry context, the user question, and
        response guidance.
    """
    context_block = format_telemetry_context(telemetry, active_year=active_year)
    return (
        f"{context_block}\n\n"
        f"User Question: {user_message}\n"
        "Provide a clear, data-grounded response."
    )