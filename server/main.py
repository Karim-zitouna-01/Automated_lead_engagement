# Automated_lead_engagement/server/main.py
from fastapi import FastAPI
from server.api.endpoints import identification
from server.api.endpoints import lead
from server.api.endpoints import service

app = FastAPI()

app.include_router(identification.router, prefix="/identification", tags=["Identification"])
app.include_router(lead.router, prefix="/lead", tags=["Lead"])
app.include_router(service.router, prefix="/services", tags=["Services"])
