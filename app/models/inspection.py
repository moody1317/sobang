import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class InspectionType(str, enum.Enum):
    화재안전 = "화재안전"
    위험물 = "위험물"
    소방시설 = "소방시설"
    피난시설 = "피난시설"
    산악대비 = "산악대비"

class InspectionStatus(str, enum.Enum):
    예정 = "예정"
    진행 = "진행"
    완료 = "완료"

class InspectionResult(str, enum.Enum):
    이상없음 = "이상없음"
    시정필요 = "시정필요"
    불합격 = "불합격"

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    target = Column(String(200), nullable=False)
    inspection_type = Column(Enum(InspectionType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(Enum(InspectionStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=InspectionStatus.예정)

    scheduled_date = Column(Date, nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(String(500), nullable=True)

    result = Column(Enum(InspectionResult, values_callable=lambda x: [e.value for e in x]), nullable=True)
    result_detail = Column(String(500), nullable=True)
    next_inspection_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)