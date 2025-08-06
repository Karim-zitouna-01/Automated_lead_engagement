# Automated_lead_engagement/server/services/identification_service.py
from firebase_admin import firestore
from server.common.firebase_config import get_firestore_db
from celery import shared_task
from server.common.celery_config import celery_app
from Lead_Identification.integration.identification import run_lead_pipeline

db= get_firestore_db()

@celery_app.task
def run_pipeline_task(icp: dict, service_id: str):
    print("Running pipeline task***")
    db= get_firestore_db()
    try:
        print(f"Running lead pipeline for service_id: {service_id} with ICP: {icp}")
        run_lead_pipeline(icp, service_id)
        db.collection("services").document(service_id).update({"generation_status": "done"})
    except Exception as e:
        db.collection("services").document(service_id).update({"generation_status": "error"})
        raise e


def get_icp(service_id: str) -> dict:
    doc = db.collection("services").document(service_id).get()
    if doc.exists:
        return doc.to_dict().get("icp")
    else:
        raise ValueError("Service not found")

def update_generation_status(service_id: str, status: str):
    db.collection("services").document(service_id).update({"generation_status": status})

def generate_leads(service_id: str):
    try:
        print(f"Generating leads for service_id: {service_id}")
        update_generation_status(service_id, "in_progress")
        print(f"Fetching ICP for service_id: {service_id}")
        icp = get_icp(service_id)
        print(f"ICP fetched")
        print(f"Running pipeline task for service_id: {service_id}")
        run_pipeline_task.delay(icp, service_id)
    except Exception as e:
        update_generation_status(service_id, "error")
        print(f"Error generating leads for service_id {service_id}: {e}")
        raise e
