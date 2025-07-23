# main.py
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv # Explicitly load .env

load_dotenv() # Load environment variables

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any

from core.config import settings # Import settings first
from core.graph_pipeline import run_graph as run_lead_finding_graph, run_sales_coach_graph

# --- Logging setup ---
logger = logging.getLogger("lead_api")
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)
fh = RotatingFileHandler("backend.log", maxBytes=5 * 1024 * 1024, backupCount=2)
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)

logger.addHandler(ch)
logger.addHandler(fh)
for name in ("uvicorn.error", "uvicorn.access"):
    log = logging.getLogger(name)
    log.handlers = [ch, fh]

# --- App init ---
app = FastAPI(
    title="LeadEngagement API", 
    version="2.0.0",
    description="An API for finding and qualifying leads, and for coaching sales teams."
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Request models ---
class LeadFinderRequest(BaseModel):
    service_name: str

class SalesCoachRequest(BaseModel):
    company_name: str
    service_name: str
    question: str

# --- Error handlers ---
@app.exception_handler(HTTPException)
async def handle_http(request: Request, exc: HTTPException):
    logger.error(f"{request.method} {request.url.path} -> {exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def handle_validation(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error for {request.method} {request.url.path}: {exc}")
    
    # Process errors to ensure they are JSON serializable
    processed_errors = []
    for error in exc.errors():
        processed_error = {}
        for key, value in error.items():
            if isinstance(value, bytes):
                processed_error[key] = value.decode('utf-8', errors='ignore') # Decode bytes to string
            else:
                processed_error[key] = value
        processed_errors.append(processed_error)

    return JSONResponse(status_code=422, content={"detail": processed_errors})

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "LeadEngagement API v2.0 is running"}

@app.post("/api/find_leads", summary="Find new potential leads")
async def find_leads(req: LeadFinderRequest):
    """
    Scans the web to find a list of potential new leads based on the ICP 
    for a given service. Returns an enriched list of companies including
    summaries, reasons for matching, and key personnel.
    """
    logger.info(f"Lead finding request for service: {req.service_name}")
    report = run_lead_finding_graph(req.service_name)
    if report.get("error"):
        raise HTTPException(status_code=500, detail=report["error"])
    return report

@app.post("/api/sales_coach", summary="Get coaching for a sales engagement")
async def sales_coach(req: SalesCoachRequest):
    """
    Acts as a sales coach. Takes a company name, a service, and a question,
    and returns a strategic answer based on a combination of a detailed
    analytical report and the Ideal Customer Profile (ICP).
    """
    logger.info(f"Sales coach request for {req.company_name} regarding {req.service_name}")
    try:
        answer = run_sales_coach_graph(req.company_name, req.service_name, req.question)
        if isinstance(answer, dict) and answer.get("error"):
             raise HTTPException(status_code=500, detail=answer["error"])
        return {"answer": answer}
    except Exception as e:
        logger.error(f"An unexpected error occurred in /sales_coach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# The old /generate_report and /chat endpoints are now deprecated and replaced by the more powerful /sales_coach endpoint.

if __name__ == "__main__":
    # To run the server: uvicorn main:app --host 0.0.0.0 --port 8002 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, log_level="info", access_log=True)
