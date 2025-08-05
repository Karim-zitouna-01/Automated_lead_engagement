from pydantic import BaseModel
from typing import Dict

class Service(BaseModel):
    id: str
    client_id: str
    service_name: str
    icp: Dict
