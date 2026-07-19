import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class IncidentType(str, enum.Enum):
    화재 = "화재"
    구조 = "구조"
    구급 = "구급"
    위험물 = "위험물"
    기타 = "기타"

class IncidentStatus(str, enum.Enum):
    신고접수 = "신고접수"
    출동중 = "출동중"
    현장도착 = "현장도착"
    종료 = "종료"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    incident_type = Column(Enum(IncidentType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(Enum(IncidentStatus, values_callable=lambda x: [e.value for e in x]), nullable=False)

    address = Column(String(255), nullable=True)
    dong_name = Column(String(50), nullable=True)
    latitude = Column(String(30), nullable=True)
    longitude = Column(String(30), nullable=True)

    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)

    reported_at = Column(DateTime, server_default=func.now(), nullable=False)
    dispatched_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    description = Column(String(500), nullable=True)
    is_simulated = Column(String(1), nullable=False, default="Y")
    is_false_alarm = Column(Boolean, nullable=False, default=False)

    fire_truck_count = Column(Integer, nullable=False, default=0)
    ambulance_count = Column(Integer, nullable=False, default=0)