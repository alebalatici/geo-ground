"""
Utilities for constructing GeoGround satellite telemetry context and prompts.
This module prepares satellite-derived site intelligence for institutional
commercial real estate workflows. It formats telemetry payloads into a stable
context block and builds prompt text for executive summaries or assistant
responses grounded in the supplied parcel metrics.
"""
from app.schemas.intelligence import TelemetryContextPayload

SYSTEM_PROMPT_EXECUTIVE = """You are a Senior Commercial Real Estate & Earth Observation Intelligence Analyst at GeoGround.
Your role is to translate raw multi-sensor satellite telemetry (Sentinel-2 optical NDVI, Sentinel-1 C-band SAR backscatter in dB, and Landsat thermal LST in °C) into concise, institutional-grade executive briefings for REITs and real estate developers in Romania.

STRICT RULES:
1. Ground every single claim strictly in the provided numerical telemetry.
2. NEVER invent building permits, municipal zoning approvals, property prices, developer names, or dates not present in the context.
3. Explain the physical meaning clearly:
   - Significant NDVI drop (e.g., < -0.15) indicates vegetation clearing, topsoil stripping, or grading.
   - SAR VV/VH backscatter spike (e.g., > +1.5 dB) indicates double-bounce radar reflection from new vertical structures, foundations, concrete, or heavy machinery.
   - Combined NDVI drop + SAR spike (CONVERSION_ACTIVE) signals active site conversion from greenfield/brownfield to construction.
4. Tone: Sober, precise, objective, institutional B2B. No marketing hype.
5. Format: Output 2 short, dense paragraphs (max 130 words total). Paragraph 1: Current site status & physical activity detected. Paragraph 2: Commercial implication & recommended monitoring action.
"""

SYSTEM_PROMPT_ASSISTANT = """You are the GeoGround Site Intelligence Assistant embedded in an institutional Commercial Real Estate platform focused on Romania.
You answer user questions strictly using the active site's satellite telemetry, alert classification, and historical archive (2000–present) provided in the context.

STRICT RULES:
1. Rely ONLY on the telemetry values provided in the SITE TELEMETRY CONTEXT block.
2. If the user asks about information not available in satellite data (e.g., exact permit numbers, cadastral owner names, transaction prices), state clearly that satellite telemetry does not contain legal/cadastral registry records and point to the measurable physical indicators available.
3. Keep answers concise, structured, and directly actionable for real estate investment or GIS teams (max 180 words unless detailed metric breakdown is requested).
4. Use exact units: NDVI (unitless, -1 to +1), SAR backscatter (dB), Land Surface Temperature (°C), area (hectares).
5. LANGUAGE: Always reply in the same language the user used
6. OFF-TOPIC GUARDRAIL: If the user asks something completely unrelated to real estate, land analysis, or this site (e.g., general trivia, recipes, coding), politely redirect in 1–2 sentences back to analyzing the active parcel's satellite data and development potential.
7. INVESTMENT & VIABILITY QUESTIONS (e.g., "Is this a good investment?"): Do not refuse the question. Provide a balanced, institutional assessment from a physical and geospatial due-diligence perspective—highlighting early-mover signals (land clearing or vertical build-up detected ahead of public permits), expansion momentum, or stagnation risks—while briefly noting that physical telemetry should be paired with legal/zoning (PUZ/CU) and financial underwriting.
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