from firebase_admin import firestore
from server.common.firebase_config import get_firestore_db
from celery import shared_task
from Lead_Identification.integration.identification import run_lead_pipeline

db = get_firestore_db()

@shared_task
def run_pipeline_task(icp: dict, service_id: str):
    db = get_firestore_db()
    try:
        run_lead_pipeline(icp)
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
        update_generation_status(service_id, "in_progress")
        icp = get_icp(service_id)
        run_pipeline_task.delay(icp, service_id)
    except Exception as e:
        update_generation_status(service_id, "error")
        raise e
