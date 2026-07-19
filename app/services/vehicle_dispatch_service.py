from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentStatus, IncidentType
from app.models.incident_dispatch import DispatchRole
from app.models.incident_vehicle_assignment import IncidentVehicleAssignment
from app.models.rescue_unit import RescueUnit
from app.models.safety_center import SafetyCenter
from app.models.vehicle import Vehicle, VehicleType

VEHICLE_CREW_SIZE = {
    VehicleType.중형펌프차: 5,
    VehicleType.대형펌프차: 5,
    VehicleType.소형펌프차: 3,
    VehicleType.물탱크차: 2,
    VehicleType.화학차: 5,
    VehicleType.조연차: 3,
    VehicleType.소형사다리차: 3,
    VehicleType.고가차: 3,
    VehicleType.굴절차: 3,
    VehicleType.구급차: 3,
    VehicleType.음압구급차: 3,
    VehicleType.생활안전구조차: 3,
    VehicleType.구조공작차: 5,
    VehicleType.구조버스: 25,
    VehicleType.오토바이: 1,
    VehicleType.순찰차: 5,
    VehicleType.트레일러: 0,
}

INCIDENT_VEHICLE_TYPES = {
    IncidentType.화재: [VehicleType.중형펌프차, VehicleType.소형펌프차, VehicleType.대형펌프차, VehicleType.물탱크차],
    IncidentType.구조: [VehicleType.구조공작차, VehicleType.생활안전구조차],
    IncidentType.구급: [VehicleType.구급차, VehicleType.음압구급차],
    IncidentType.위험물: [VehicleType.화학차],
    IncidentType.기타: [VehicleType.순찰차],
}

def get_vehicle_assignments(db: Session, incident_id: int) -> list[dict]:
    items = db.query(IncidentVehicleAssignment).filter(IncidentVehicleAssignment.incident_id == incident_id).all()
    return [
        {
            "id": v.id,
            "vehicle_type": v.vehicle_type.value,
            "unit_role": v.unit_role.value,
            "unit_name": v.unit_name,
            "required_crew": v.required_crew,
        }
        for v in items
    ]

def _count_active_assignments(db: Session, vehicle_type: VehicleType, safety_center_id: int | None, rescue_unit_id: int | None) -> int:
    query = (
        db.query(IncidentVehicleAssignment)
        .join(Incident, IncidentVehicleAssignment.incident_id == Incident.id)
        .filter(
            IncidentVehicleAssignment.vehicle_type == vehicle_type,
            Incident.status != IncidentStatus.종료,
            Incident.is_false_alarm == False,  # noqa: E712
        )
    )
    if safety_center_id is not None:
        query = query.filter(IncidentVehicleAssignment.safety_center_id == safety_center_id)
    else:
        query = query.filter(IncidentVehicleAssignment.rescue_unit_id == rescue_unit_id)
    return query.count()

def assign_vehicles_for_incident(db: Session, incident: Incident, station_id: int) -> list[IncidentVehicleAssignment]:
    needed_types = INCIDENT_VEHICLE_TYPES.get(incident.incident_type, [])
    if not needed_types:
        return []

    if incident.incident_type == IncidentType.구조:
        unit = db.query(RescueUnit).filter(RescueUnit.parent_station_id == station_id).first()
        unit_role = DispatchRole.rescuer
    elif incident.safety_center_id:
        unit = db.query(SafetyCenter).filter(SafetyCenter.id == incident.safety_center_id).first()
        unit_role = DispatchRole.firefighter
    else:
        unit = None
        unit_role = None

    if not unit:
        return []

    is_rescue = incident.incident_type == IncidentType.구조
    safety_center_id = None if is_rescue else unit.id
    rescue_unit_id = unit.id if is_rescue else None

    unit_filter = Vehicle.rescue_unit_id == unit.id if is_rescue else Vehicle.safety_center_id == unit.id
    vehicles = db.query(Vehicle).filter(unit_filter, Vehicle.vehicle_type.in_(needed_types)).all()

    assignments = []
    for vehicle in vehicles:
        active = _count_active_assignments(db, vehicle.vehicle_type, safety_center_id, rescue_unit_id)
        available = max(0, vehicle.count - active)
        for _ in range(available):
            assignment = IncidentVehicleAssignment(
                incident_id=incident.id,
                vehicle_type=vehicle.vehicle_type,
                unit_role=unit_role,
                unit_name=unit.station_name,
                required_crew=VEHICLE_CREW_SIZE[vehicle.vehicle_type],
                safety_center_id=safety_center_id,
                rescue_unit_id=rescue_unit_id,
            )
            db.add(assignment)
            assignments.append(assignment)

    return assignments
