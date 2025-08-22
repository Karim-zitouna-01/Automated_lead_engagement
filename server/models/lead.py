from pydantic import BaseModel
from typing import List
from typing import Optional

class KeyPersonal(BaseModel):
    name: str
    role: Optional[str] = ""

class Lead(BaseModel):
    id: str
    company_name: str
    key_personals: Optional[List[KeyPersonal]] = None
    report_url: Optional[str] = ""
    qualification_url: Optional[str] = ""
    service_id: str 
