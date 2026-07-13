# app/models/ems_hourly_stat.py
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class EmsHourlyStat(Base):
    __tablename__ = "ems_hourly_stats"

    id = Column(Integer, primary_key=True)
    station_name = Column(String(200))   # 우리 DB 기준 이름 ("청주동부소방서")
    stmt_ym = Column(String(6))          # 신고년월
    hour = Column(Integer)               # 0~23
    count = Column(Integer)