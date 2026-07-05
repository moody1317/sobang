from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.core.database import Base

class ActiveRiskEvent(Base):
    __tablename__ = "active_risk_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(20))
    epicenter_lat = Column(Numeric(10, 6))
    epicenter_lon = Column(Numeric(10, 6))
    magnitude = Column(Numeric(3, 1))
    affected_radius_km = Column(Numeric(6, 1))
    occurred_at = Column(DateTime)
    expires_at = Column(DateTime)