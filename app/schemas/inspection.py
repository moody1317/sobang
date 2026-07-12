from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.models.inspection import InspectionType, InspectionStatus, InspectionResult

class InspectionCreate(BaseModel):
    jurisdiction_id: int
    target: str
    inspection_type: InspectionType
    scheduled_date: date
    note: Optional[str] = None

class InspectionCompleteRequest(BaseModel):
    result: InspectionResult
    result_detail: Optional[str] = None
    next_inspection_date: Optional[date] = None

class InspectionResponse(BaseModel):
    id: int
    jurisdiction_id: int
    ward_name: Optional[str] = None
    target: str
    inspection_type: InspectionType
    status: InspectionStatus
    scheduled_date: date
    inspector_id: int
    inspector_name: Optional[str] = None
    note: Optional[str] = None
    result: Optional[InspectionResult] = None
    result_detail: Optional[str] = None
    next_inspection_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True