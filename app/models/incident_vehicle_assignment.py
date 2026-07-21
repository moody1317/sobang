from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from app.core.database import Base
from app.models.vehicle import VehicleType
from app.models.incident_dispatch import DispatchRole

class IncidentVehicleAssignment(Base):
    __tablename__ = "incident_vehicle_assignments"

    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    vehicle_type = Column(Enum(VehicleType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    unit_role = Column(Enum(DispatchRole, values_callable=lambda x: [e.value for e in x]), nullable=False)
    unit_name = Column(String(100), nullable=False)
    required_crew = Column(Integer, nullable=False)
    safety_center_id = Column(Integer, ForeignKey("safety_centers_v2.id"), nullable=True)
    rescue_unit_id = Column(Integer, ForeignKey("rescue_units.id"), nullable=True)
    reason = Column(String(200), nullable=True)
