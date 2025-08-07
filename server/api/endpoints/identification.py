# Automated_lead_engagement/server/api/endpoints/identification.py
from fastapi import APIRouter, HTTPException
from server.services.identification_service import generate_leads

router = APIRouter()

@router.post("/generate_leads/{service_id}")
def generate_leads_endpoint(service_id: str):
    try:
        print(f"Request to generate leads for service_id: {service_id}")
        generate_leads(service_id)
        return {"message": "Lead generation started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
