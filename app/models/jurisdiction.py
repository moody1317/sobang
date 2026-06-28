from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.core.database import Base


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id = Column(Integer, primary_key=True)
    ward_id = Column(String(30), unique=True, nullable=False)   # VWorld 고유 ID
    ward_name = Column(String(100), nullable=False)              # ex) "중앙119안전센터"

    station_id = Column(Integer, ForeignKey("stations.id"), nullable=True)
    safety_center_id = Column(Integer, ForeignKey("safety_centers.id"), nullable=True)

    geometry = Column(JSON, nullable=False)   # MultiPolygon GeoJSON 좌표