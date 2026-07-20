import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class DispatchRole(str, enum.Enum):
    firefighter = "firefighter"
    rescuer = "rescuer"

class IncidentDispatch(Base):
    __tablename__ = "incident_dispatches"
    __table_args__ = (UniqueConstraint("incident_id", "user_id", name="uq_incident_user"),)

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_role = Column(Enum(DispatchRole, values_callable=lambda x: [e.value for e in x]), nullable=False)

    dispatched_at = Column(DateTime, server_default=func.now(), nullable=False)
    returned_at = Column(DateTime, nullable=True)
    activity_note = Column(String(500), nullable=True)
    equipment_used = Column(String(200), nullable=True)
    reported_false_alarm = Column(Boolean, nullable=True)
