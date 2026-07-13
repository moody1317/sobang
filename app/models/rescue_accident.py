from sqlalchemy import Column, Integer, String, Date, Time
from app.core.database import Base

class RescueAccident(Base):
    __tablename__ = "rescue_accidents"

    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=True)
    report_time = Column(Time, nullable=True)
    dispatch_date = Column(Date, nullable=True)
    dispatch_time = Column(Time, nullable=True)

    sido_nm = Column(String(40), nullable=True)
    gu_nm = Column(String(40), nullable=True)
    dong_nm = Column(String(40), nullable=True)

    accident_cause = Column(String(20), nullable=True)
    accident_type_nm = Column(String(50), nullable=True)