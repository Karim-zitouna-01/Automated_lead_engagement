# launch.py
import sys
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
from core.pipeline import LeadGenerationPipeline
from pydantic import BaseModel
from typing import Dict, Any

# --- Configuration du logger ---
logger = logging.getLogger("launch")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

# --- Définition des modèles Pydantic ---
class ReportRequest(BaseModel):
    company_name: str
    icp: Dict[str, Any]

class ChatRequest(BaseModel):
    question: str
    report_context: Dict[str, Any]

# --- Initialisation de l'application FastAPI ---
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/api/generate_report")
async def generate_report(req: ReportRequest):
    logger.info(f"Requête de génération de rapport pour {req.company_name}")
    pipeline = LeadGenerationPipeline(icp=req.icp)
    report = pipeline.generate_report(req.company_name)
    if report.get("error"):
        logger.error(f"Erreur lors de la génération du rapport : {report['error']}")
        return {"error": report["error"]}
    return report

@app.post("/api/chat")
async def chat(req: ChatRequest):
    logger.info("Requête de chat reçue")
    pipeline = LeadGenerationPipeline()
    answer = pipeline.answer_question_with_rag(req.question, req.report_context)
    return {"answer": answer}

# --- Fonction de test interne ---
def run_tests():
    logger.info("🏁 Exécution des tests internes via TestClient")
    client = TestClient(app)

    # Test de l'endpoint /api/generate_report
    logger.info("🔹 Test de /api/generate_report")
    response = client.post("/api/generate_report", json={
        "company_name": "Acme Corp",
        "icp": {"ideal_customer_profile": {"industry": "Tech"}}
    })
    logger.info(f"Statut HTTP : {response.status_code}")
    logger.info("Réponse JSON :")
    logger.info(response.json())

    # Test de l'endpoint /api/chat
    logger.info("🔹 Test de /api/chat")
    dummy_report = {"company_summary": "Test", "business_signals": ["signal A"]}
    response = client.post("/api/chat", json={
        "question": "Quels signaux business ?",
        "report_context": dummy_report
    })
    logger.info(f"Statut HTTP : {response.status_code}")
    logger.info("Réponse JSON :")
    logger.info(response.json())

if __name__ == "__main__":
    run_tests()
# launch.py