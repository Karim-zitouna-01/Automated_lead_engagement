from pydantic import BaseModel
from typing import List

class KeyPersonal(BaseModel):
    name: str
    role: str

class Lead(BaseModel):
    id: str
    company_name: str
    key_personals: List[KeyPersonal]
    report_url: str
    qualification_url: str
    service_id: str
