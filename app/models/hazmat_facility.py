from sqlalchemy import Column, Integer, String, Numeric
from app.core.database import Base

class HazmatFacility(Base):
    __tablename__ = "hazmat_facilities"

    id = Column(Integer, primary_key=True)
    objt_id = Column(Integer, unique=True, nullable=False)
    entrps_nm = Column(String(200))
    induty_nm = Column(String(200))
    adres = Column(String(300))
    rn_adres = Column(String(300))
    ctprvn_cd = Column(Integer, nullable=True)
    sgg_cd = Column(Integer, nullable=True)
    emd_cd = Column(Integer, nullable=True)
    latitude = Column(Numeric(10, 7), nullable=True)
    longitude = Column(Numeric(10, 7), nullable=True)
    bsum = Column(Numeric(14, 2), nullable=True)
