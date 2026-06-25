from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class SafetyCenter(Base):
    __tablename__ = "safety_centers"

    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    center_name = Column(String(100), nullable=False)   # 119안전센터명
    address = Column(String(255))
    phone_number = Column(String(20))
    fax_number = Column(String(20))