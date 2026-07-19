import enum
from sqlalchemy import Column, Integer, Enum, ForeignKey
from app.core.database import Base

class VehicleType(str, enum.Enum):
    중형펌프차 = "중형펌프차"
    소형펌프차 = "소형펌프차"
    대형펌프차 = "대형펌프차"
    물탱크차 = "물탱크차"
    화학차 = "화학차"
    조연차 = "조연차"
    소형사다리차 = "소형사다리차"
    고가차 = "고가차"
    굴절차 = "굴절차"
    구급차 = "구급차"
    음압구급차 = "음압구급차"
    생활안전구조차 = "생활안전구조차"
    구조공작차 = "구조공작차"
    구조버스 = "구조버스"
    오토바이 = "오토바이"
    순찰차 = "순찰차"
    트레일러 = "트레일러"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    vehicle_type = Column(Enum(VehicleType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)
    rescue_unit_id = Column(Integer, ForeignKey("rescue_units.id"), nullable=True)
    count = Column(Integer, nullable=False, default=1)
