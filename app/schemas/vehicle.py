from typing import Optional
from pydantic import BaseModel, Field
from app.models.vehicle import VehicleType

class VehicleCreate(BaseModel):
    vehicle_type: VehicleType
    count: int = Field(default=1, ge=1)
    safety_center_id: Optional[int] = None
    rescue_unit_id: Optional[int] = None

class VehicleUpdate(BaseModel):
    count: int = Field(ge=1)
