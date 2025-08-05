from fastapi import FastAPI
from server.api.endpoints import identification

app = FastAPI()

app.include_router(identification.router, prefix="/identification", tags=["Identification"])
