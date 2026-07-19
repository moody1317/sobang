from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class RescueUnit(Base):
    __tablename__ = "rescue_units"
    id = Column(Integer, primary_key=True)
    station_code = Column(String(30), unique=True)
    station_name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone_number = Column(String(20))
    parent_station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
