#server.services.service_service.py
# server/services/service_service.py

from server.common.firebase_config import get_firestore_db
from server.models.service import Service
import uuid
from typing import Optional, Dict
db= get_firestore_db()

def add_service(service: Service):
    service_dict = service.dict()
    service_ref = db.collection("services").document(service.id)
    service_ref.set(service_dict)
    return service


def delete_service(service_id: str):
    db.collection("services").document(service_id).delete()


def change_icp(service_id: str, icp: Dict):
    service_ref = db.collection("services").document(service_id)
    service_ref.update({"icp": icp})

def get_service(service_id: str) -> Optional[Service]:
    service_ref = db.collection("services").document(service_id)
    service_data = service_ref.get().to_dict()
    if service_data:
        return Service(**service_data)
    return None

def get_all_services() -> list[Service]:
    print("Fetching all services")
    services_ref = db.collection("services").stream()
    if not services_ref:
        print("No services found")
        return []
    print("Services found")
    services = []
    for service in services_ref:
        service_data = service.to_dict()
        services.append(Service(**service_data))
    return services
