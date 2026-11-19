from fastapi import APIRouter

from app import schemas
from app.services import industry_demand

router = APIRouter(prefix="/industry", tags=["Industry Demand Analyzer"])


@router.get("/demand", response_model=schemas.IndustryDemandOut)
def get_demand():
    return industry_demand.get_industry_demand()
