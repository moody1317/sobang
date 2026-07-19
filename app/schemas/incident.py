from typing import Optional
from pydantic import BaseModel

class IncidentReturnRequest(BaseModel):
    activity_note: str
    equipment_used: Optional[str] = None
