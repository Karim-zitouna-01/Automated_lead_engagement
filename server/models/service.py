from pydantic import BaseModel
from typing import Dict

class Service(BaseModel):
    id: str
    client_id: str
    service_name: str
    icp: Dict
<<<<<<< HEAD
    genration_status: str
=======
>>>>>>> 360820597b4a33837bb12a4b6af43a4c4719dd47
