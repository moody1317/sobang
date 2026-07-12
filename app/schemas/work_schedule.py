from datetime import date as date_type, time
from typing import Optional
from pydantic import BaseModel
from app.models.work_schedule import ShiftType

class WorkScheduleUpsert(BaseModel):
    shift_type: ShiftType
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_patrol: bool = False
    is_education: bool = False

class WorkScheduleResponse(BaseModel):
    date: date_type
    shift_type: ShiftType
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_patrol: bool
    is_education: bool

    class Config:
        from_attributes = True