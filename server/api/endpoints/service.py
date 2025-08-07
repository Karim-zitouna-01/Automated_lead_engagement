#server.api.endpoints.service.py
# server/api/endpoints/service.py

from fastapi import APIRouter, HTTPException
from typing import Optional, Dict
from server.models.service import Service
from server.services.service_service import (
    add_service, delete_service, change_icp, get_service, get_all_services
)

router = APIRouter()

@router.post("/add/", response_model=Service)
def create_service(service: Service):
    return add_service(service)


@router.delete("/delete/{service_id}")
def remove_service(service_id: str):
    delete_service(service_id)
    return {"message": "Service deleted successfully"}


@router.put("/update_icp/{service_id}")
def update_service_icp(service_id: str, icp: Dict):
    try:
        change_icp(service_id, icp)
        return {"message": "ICP updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{service_id}", response_model=Service)
def get_service_by_id(service_id: str):
    service = get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.get("/all/", response_model=list[Service])
def get_all():
    print("Fetching all services--api endpoint")
    services = get_all_services()
    if not services:
        raise HTTPException(status_code=404, detail="No services found")
    return services
