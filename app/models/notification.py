from enum import Enum as PyEnum
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.sql import func
from app.core.database import Base


class NotificationLevel(PyEnum):
    SAFE = "안전"
    CAUTION = "주의"
    WARNING = "경계"
    DANGER = "위험"
    ALERT = "특보"

class NotificationType(str, PyEnum):
    위험스코어변동 = "위험스코어변동"
    기상특보 = "기상특보"
    지진 = "지진"
    출동접수 = "출동접수"
    진압완료 = "진압완료"
    점검기한 = "점검기한"
    순찰예측 = "순찰예측"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    level = Column(
        SAEnum(NotificationLevel, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    title = Column(String(100), nullable=False)
    message = Column(String(500), nullable=False)
    source = Column(String(30), nullable=False)  # incident / weather / inspection / risk_score
    related_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)