from sqlalchemy import Column, Integer, String, UniqueConstraint
from app.core.database import Base

class AdminDongPopulation(Base):
    __tablename__ = "admin_dong_populations"
    __table_args__ = (UniqueConstraint("admin_code", "std_ym", name="uq_admin_dong_stdym"),)

    id = Column(Integer, primary_key=True)
    admin_code = Column(String(20), index=True)   # admmCd — 행정동코드
    sido_nm = Column(String(50))                    # ctpvNm
    sigungu_nm = Column(String(50))                  # sggNm
    dong_nm = Column(String(50))                     # dongNm — 여기서 "복대1동"/"복대2동" 분리 기대
    std_ym = Column(String(6))                       # statsYm

    total_ppltn = Column(Integer)
    male_ppltn = Column(Integer)
    female_ppltn = Column(Integer)
    elderly_ppltn = Column(Integer)