from sqlalchemy import Column, Integer, String, Numeric
from app.core.database import Base

class ForestFireRisk(Base):
    __tablename__ = "forest_fire_risks"

    id = Column(Integer, primary_key=True)
    sigu_code = Column(String(5), unique=True, index=True)
    sido_nm = Column(String(40))
    sigungu_nm = Column(String(40))
    upplocalcd = Column(String(2))

    mean_index = Column(Numeric(6, 2))
    max_index = Column(Numeric(6, 2))
    min_index = Column(Numeric(6, 2))
    std_index = Column(Numeric(6, 2))

    area_low = Column(Numeric(12, 2))
    area_mid = Column(Numeric(12, 2))
    area_high = Column(Numeric(12, 2))
    area_very_high = Column(Numeric(12, 2))

    analdate = Column(String(20))