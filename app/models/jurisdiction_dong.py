# app/models/jurisdiction_dong.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from app.core.database import Base

class JurisdictionDong(Base):
    __tablename__ = "jurisdiction_dongs"

    id = Column(Integer, primary_key=True)
    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=False)
    sigungu_nm = Column(String(40), nullable=False)
    dong_nm = Column(String(40), nullable=False)
    display_name = Column(String(40), nullable=True)
    split_ratio = Column(Numeric(4, 3), nullable=False, default=1.0)