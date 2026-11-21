from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies import get_intelligence_service
from app.schemas.intelligence import (
    ExecutiveSummaryResponse,
    SiteChatRequest,
    SiteChatResponse,
)
from app.services.intelligence_service import IntelligenceService, SiteNotFoundError

router = APIRouter(prefix="/sites/{site_id}", tags=["AI Executive & Assistant"])


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryResponse,
    summary="Generate Gemini executive intelligence brief for a site",
)
def get_executive_summary(
    site_id: str,
    service: IntelligenceService = Depends(get_intelligence_service),
) -> ExecutiveSummaryResponse:
    """Translate raw satellite telemetry deltas into an institutional investor brief."""
    try:
        return service.get_site_executive_summary(site_id)
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/chat",
    response_model=SiteChatResponse,
    summary="Ask the contextual site intelligence assistant",
)
def chat_with_site_assistant(
    site_id: str,
    request: SiteChatRequest,
    service: IntelligenceService = Depends(get_intelligence_service),
) -> SiteChatResponse:
    """
    Answer investor or GIS questions grounded strictly in active site telemetry.
    """
    try:
        return service.answer_site_chat(site_id=site_id, request=request)
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc