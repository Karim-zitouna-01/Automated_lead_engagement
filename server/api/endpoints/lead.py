from fastapi import APIRouter, HTTPException, Query
from typing import List
from server.services.lead_service import get_all_leads
from server.models.lead import Lead

router = APIRouter()

@router.get("/leads", response_model=List[Lead])
def get_leads_endpoint(service_id: str = Query(...)):
    try:
        leads = get_all_leads(service_id)
        return leads
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while retrieving leads.")
