from pydantic import BaseModel

class Client(BaseModel):
    id: str
    client_name: str
