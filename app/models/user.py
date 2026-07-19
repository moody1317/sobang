from enum import Enum as PyEnum
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class UnitType(PyEnum):
    HEADQUARTERS = "본서"
    SAFETY_CENTER = "안전센터"
    AMBULANCE = "구급대"
    AVIATION = "항공대"
    SPECIAL_RESPONSE = "특수대응단"
    LOCAL_UNIT = "지역대"
    RESCUE_SQUAD = "119구조대"
    OTHER = "기타"

class Department(PyEnum):
    ADMINISTRATION = "소방행정과"
    DISASTER_RESPONSE = "재난대응과"
    PREVENTION_SAFETY = "예방안전과"
    FIELD_RESPONSE = "현장대응단"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firefighter_number = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="firefighter")
    rank = Column(String(30), nullable=True)
    phone_number = Column(String(30), nullable=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    unit_type = Column(
        SAEnum(UnitType, values_callable=lambda x: [e.value for e in x]),
        default=UnitType.HEADQUARTERS,
        nullable=False,
    )
    safety_center_id = Column(Integer, nullable=True)
    department = Column(
        SAEnum(Department, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    local_unit_id = Column(Integer, ForeignKey("local_units.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    must_change_password = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    station = relationship("Station")