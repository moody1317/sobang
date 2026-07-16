# app/models/admin_dong_boundary.py
from sqlalchemy import Column, Integer, String, JSON, Numeric, DateTime
from app.core.database import Base


class AdminDongBoundary(Base):
    __tablename__ = "admin_dong_boundaries"

    id = Column(Integer, primary_key=True)
    admin_code = Column(String(20), unique=True, nullable=False)   # 행정동코드 — AdminDongPopulation.admin_code와 동일 체계
    dong_nm = Column(String(50), nullable=False)
    sigungu_nm = Column(String(50))
    sido_nm = Column(String(50))

    geometry = Column(JSON, nullable=True)   # GeoJSON 미매칭 동은 NULL로 남김

    risk_score = Column(Numeric(5, 2), nullable=True)
    risk_score_breakdown = Column(JSON, nullable=True)
    risk_score_updated_at = Column(DateTime, nullable=True)
