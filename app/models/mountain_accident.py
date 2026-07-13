# app/models/mountain_accident.py
from sqlalchemy import Column, Integer, String, Date, Time
from app.core.database import Base


class MountainAccident(Base):
    __tablename__ = "mountain_accidents"

    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=True)
    report_time = Column(Time, nullable=True)

    sido_nm = Column(String(40), nullable=True)      # 발생장소_시
    gu_nm = Column(String(40), nullable=True)         # 발생장소_구 (예: "청주시 상당구")
    dong_nm = Column(String(40), nullable=True)       # 발생장소_동
    ri_nm = Column(String(40), nullable=True)         # 발생장소_리

    accident_cause = Column(String(20), nullable=True)
    accident_type_nm = Column(String(50), nullable=True)   # 사고원인코드명_사고종별
    result_cd = Column(String(200), nullable=True)         # 처리결과코드
    rescued_count = Column(Integer, nullable=True)