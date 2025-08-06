from typing import List
from firebase_admin import firestore
from server.common.firebase_config import get_firestore_db
from server.models.lead import Lead  # assuming Lead model is defined using Pydantic

db = get_firestore_db()

def get_all_leads(service_id: str) -> List[Lead]:
    # Check if generation is done
    service_doc = db.collection("services").document(service_id).get()
    if not service_doc.exists:
        raise ValueError("Service not found")

    service_data = service_doc.to_dict()
    if service_data.get("generation_status") != "done":
        raise ValueError("Lead generation not completed yet")

    # Fetch leads with matching service_id
    leads_docs = db.collection("leads").where("service_id", "==", service_id).stream()
    leads = []

    for doc in leads_docs:
        lead_data = doc.to_dict()
        lead_data["id"] = doc.id  # make sure id is included
        leads.append(Lead(**lead_data))

    return leads
