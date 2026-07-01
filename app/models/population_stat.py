# app/models/population_stat.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.core.database import Base

class PopulationStat(Base):
    __tablename__ = "population_stats"
    __table_args__ = (UniqueConstraint("admin_code", "std_ym", name="uq_admin_code_stdym"),)

    id = Column(Integer, primary_key=True)
    admin_code = Column(String(20), index=True)   # 행정기관코드 — jurisdiction 매칭 키 후보
    sido_nm = Column(String(50))
    sigungu_nm = Column(String(50))
    hjd_nm = Column(String(50))                    # 행정동명
    std_ym = Column(String(6))                      # 기준연월

    total_ppltn = Column(Integer)
    male_ppltn = Column(Integer)
    female_ppltn = Column(Integer)
    elderly_ppltn = Column(Integer)   # 만65세 이상 남+여 합산 (연령 구간 합산해서 저장)

    jurisdiction_id = Column(Integer, ForeignKey("jurisdictions.id"), nullable=True)