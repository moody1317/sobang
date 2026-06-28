# 소방서 DB
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    station_code = Column(String(20), unique=True, nullable=False, index=True)
    station_name = Column(String(100), nullable=False)
    fclty_ty = Column(String(50), nullable=True)
    unit_type = Column(String(20), nullable=True)
    region_name = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(30), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )