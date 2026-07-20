import enum
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class LeaveType(str, enum.Enum):
    육아휴직 = "육아휴직"
    질병휴직 = "질병휴직"
    공무상질병휴직 = "공무상질병휴직"
    가사휴직 = "가사휴직"
    동반휴직 = "동반휴직"
    기타휴직 = "기타휴직"

class UserLeave(Base):
    __tablename__ = "user_leaves"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type = Column(Enum(LeaveType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    start_date = Column(Date, nullable=False)
    expected_end_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
