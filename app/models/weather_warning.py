from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class WeatherWarning(Base):
    __tablename__ = "weather_warnings"

    id = Column(Integer, primary_key=True)
    area_code = Column(String(10))          # 원본 특보구역코드 (세분구역 포함)
    area_name = Column(String(50))          # 원본 구역명
    sigungu_name = Column(String(40))       # 상위 시군구로 승격된 이름 — 관할구역 매칭용
    warn_var = Column(Integer)              # 특보종류 코드 (1~12)
    warn_stress = Column(Integer)           # 0=주의보, 1=경보
    command = Column(Integer)               # 1=발표, 2=해제 등
    cancel = Column(String(1))              # 0=정상, 1=취소
    tm_fc = Column(String(14))              # 발표시각
    start_time = Column(String(14))
    end_time = Column(String(14))