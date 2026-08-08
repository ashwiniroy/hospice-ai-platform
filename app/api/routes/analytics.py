from fastapi import APIRouter

from app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


analytics_service = AnalyticsService()


@router.get("/summary")
def get_summary():

    return analytics_service.get_summary()


@router.get("/states")
def get_hospices_by_state():

    return analytics_service.get_hospices_by_state()


@router.get("/organization-types")
def get_organization_types():

    return analytics_service.get_organization_types()