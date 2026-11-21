"""REST endpoints for monitored sites, 2000-present timelines, spectral correlations, and CSV exports."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import get_site_service
from app.schemas.site import (
    SiteCreateRequest,
    SiteDetailResponse,
    SiteListItemResponse,
    SiteTimelineResponse,
    SpectralCorrelationResponse,
)
from app.services.intelligence_service import SiteNotFoundError
from app.services.site_service import InvalidSitePolygonError, SiteService

router = APIRouter(prefix="/sites", tags=["Sites & EO Telemetry"])


@router.get(
    "",
    response_model=list[SiteListItemResponse],
    summary="List monitored commercial real-estate sites",
)
def list_sites(
    city: str | None = Query(
        default=None,
        description="Filter parcels by Romanian hub city (e.g., Cluj-Napoca, Bucharest, Timișoara).",
    ),
    service: SiteService = Depends(get_site_service),
) -> list[SiteListItemResponse]:
    """Return all monitored parcels with GeoJSON polygons and latest alert badges."""
    return service.list_monitored_sites(city=city)


@router.post(
    "",
    response_model=SiteDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register and analyze a custom site polygon",
)
def create_site(
    payload: SiteCreateRequest,
    service: SiteService = Depends(get_site_service),
) -> SiteDetailResponse:
    """Validate GeoJSON polygon within Romania bounds, store in PostGIS, and run EO pipeline."""
    try:
        return service.create_and_analyze_site(payload)
    except InvalidSitePolygonError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{site_id}",
    response_model=SiteDetailResponse,
    summary="Get detailed metadata for a monitored site",
)
def get_site_detail(
    site_id: str,
    service: SiteService = Depends(get_site_service),
) -> SiteDetailResponse:
    """Retrieve full site details, GeoJSON boundary, latest alert, and archive span."""
    try:
        return service.get_monitored_site(site_id)
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{site_id}/timeline",
    response_model=SiteTimelineResponse,
    summary="Get 2000–Present historical satellite timeline",
)
def get_site_timeline(
    site_id: str,
    start_year: int = Query(default=2000, ge=2000, le=2030),
    end_year: int | None = Query(default=None, ge=2000, le=2030),
    sensor: str | None = Query(
        default=None,
        description="Optional sensor filter (LANDSAT, SENTINEL-2, SENTINEL-1).",
    ),
    service: SiteService = Depends(get_site_service),
) -> SiteTimelineResponse:
    """Return chronological multi-sensor snapshots for the interactive Timeline Slider."""
    try:
        return service.get_site_timeline(
            site_id=site_id,
            start_year=start_year,
            end_year=end_year,
            sensor=sensor,
        )
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{site_id}/correlations",
    response_model=SpectralCorrelationResponse,
    summary="Get multispectral NDVI vs. SAR correlation analytics",
)
def get_site_correlations(
    site_id: str,
    service: SiteService = Depends(get_site_service),
) -> SpectralCorrelationResponse:
    """Return aligned optical NDVI vs. radar SAR backscatter series for Enterprise Analytics."""
    try:
        return service.get_multispectral_correlations(site_id)
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{site_id}/export/csv",
    summary="Export raw site satellite telemetry as CSV",
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "Downloadable CSV file containing raw sensor observations.",
        }
    },
)
def export_site_csv(
    site_id: str,
    service: SiteService = Depends(get_site_service),
) -> StreamingResponse:
    """Stream raw NDVI, SAR VV/VH, and thermal LST records as a downloadable CSV."""
    try:
        filename, csv_content = service.export_site_telemetry_csv(site_id)
    except SiteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )