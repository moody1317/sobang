from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    firefighter_number: str
    name: str
    email: EmailStr
    role: str = "firefighter"
    rank: Optional[str] = None
    phone_number: Optional[str] = None
    station_id: int
    is_active: bool = True
    must_change_password: bool = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "firefighter"
    rank: Optional[str] = None
    phone_number: Optional[str] = None
    station_id: int
    safety_center_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    station_name: Optional[str] = None
    unit_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserCreateResponse(UserResponse):
    temp_password: str

class ProfileUpdateRequest(BaseModel):
    current_password: str
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None