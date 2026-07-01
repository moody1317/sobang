from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from app.core.database import Base

class IncidentType(PyEnum):
    FIRE = "화재"
    RESCUE = "구조"
    EMERGENCY = "구급"
    HAZMAT = "위험물"
    OTHER = "기타"

class IncidentStatus(PyEnum):
    REPORTED = "신고접수"
    DISPATCHED = "출동중"
    ON_SCENE = "현장도착"
    RESOLVED = "종료"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    incident_type = Column(
        SAEnum(IncidentType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status = Column(
        SAEnum(IncidentStatus, values_callable=lambda x: [e.value for e in x]),
        default=IncidentStatus.REPORTED,
        nullable=False,
    )

    address = Column(String(255), nullable=True)
    dong_name = Column(String(50), nullable=True)
    latitude = Column(String(30), nullable=True)
    longitude = Column(String(30), nullable=True)

    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)

    reported_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    description = Column(String(500), nullable=True)
    is_simulated = Column(String(1), default="Y", nullable=False)  # 데모용