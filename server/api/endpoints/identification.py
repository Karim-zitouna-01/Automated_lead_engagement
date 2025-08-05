from fastapi import APIRouter, HTTPException
from server.services.identification_service import generate_leads

router = APIRouter()

@router.post("/generate_leads")
def generate_leads_endpoint(service_id: str):
    try:
        generate_leads(service_id)
        return {"message": "Lead generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
