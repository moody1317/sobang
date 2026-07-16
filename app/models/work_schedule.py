import enum
from sqlalchemy import Column, Integer, Enum, Date, Time, Boolean, ForeignKey, UniqueConstraint, String
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base

class ShiftType(str, enum.Enum):
    주간 = "주간"
    야간 = "야간"
    비번 = "비번"

class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)

    shift_type = Column(Enum(ShiftType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    is_patrol = Column(Boolean, nullable=False, default=False)
    is_education = Column(Boolean, nullable=False, default=False)
    title = Column(String(100), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)