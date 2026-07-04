# app/models/jurisdiction.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean, Numeric
from app.core.database import Base


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(Integer, primary_key=True)
    ward_id = Column(String(30), unique=True, nullable=False)
    ward_name = Column(String(100), nullable=False)

    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)   # 추가: 폐지/매칭불가 표시

    geometry = Column(JSON, nullable=False)

    allocated_total_ppltn = Column(Integer, nullable=True)
    allocated_female_ppltn = Column(Integer, nullable=True)
    allocated_elderly_ppltn = Column(Integer, nullable=True)
    population_std_ym = Column(String(6), nullable=True)

    forest_fire_risk_index = Column(Numeric(6, 2), nullable=True)