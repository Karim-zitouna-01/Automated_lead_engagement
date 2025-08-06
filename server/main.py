# Automated_lead_engagement/server/main.py
from fastapi import FastAPI
from server.api.endpoints import identification
from server.api.endpoints import lead

app = FastAPI()

app.include_router(identification.router, prefix="/identification", tags=["Identification"])
app.include_router(lead.router, prefix="/lead", tags=["Lead"])