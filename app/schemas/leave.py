from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.models.user_leave import LeaveType

class UserLeaveCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    expected_end_date: Optional[date] = None
    reason: Optional[str] = None

class UserLeaveEndRequest(BaseModel):
    end_date: Optional[date] = None
