from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UnitType, Department

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
    unit_type: UnitType = UnitType.HEADQUARTERS
    safety_center_id: Optional[int] = None
    department: Optional[Department] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    unit_type: str
    department: Optional[str] = None
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

class UserListResponse(BaseModel):
    id: int
    firefighter_number: str
    name: str
    email: EmailStr
    rank: Optional[str] = None
    phone_number: Optional[str] = None
    unit_type: str
    department: Optional[str] = None
    station_name: Optional[str] = None
    unit_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserUnitUpdateRequest(BaseModel):
    unit_type: UnitType
    safety_center_id: Optional[int] = None
    station_id: Optional[int] = None
    department: Optional[Department] = None