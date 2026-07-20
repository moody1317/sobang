from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentStatus, IncidentType
from app.models.incident_dispatch import DispatchRole
from app.models.incident_vehicle_assignment import IncidentVehicleAssignment
from app.models.jurisdiction import Jurisdiction
from app.models.rescue_unit import RescueUnit
from app.models.safety_center import SafetyCenter
from app.models.vehicle import Vehicle, VehicleType
from app.services.hazmat_facility_service import get_nearby_hazmat_facilities
from app.services.kakao_local_service import count_nearby_category

NEARBY_RADIUS_M = 1000

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

def _borrow_from_nearby_centers(
    db: Session, incident: Incident, station_id: int, vehicle_type: VehicleType, exclude_center_id: int,
) -> IncidentVehicleAssignment | None:
    """같은 소방서 산하 다른 안전센터 중 해당 차종이 남는 곳에서 1대 빌려온다.
    신고 위치와 가까운 안전센터부터 순서대로 확인 (구조대는 소방서당 1개뿐이라 대상 아님)."""
    if incident.latitude is None or incident.longitude is None:
        return None

    from shapely.geometry import shape
    from app.services.incident_service import haversine_distance

    lat, lon = float(incident.latitude), float(incident.longitude)

    centers = db.query(SafetyCenter).filter(
        SafetyCenter.parent_station_id == station_id, SafetyCenter.id != exclude_center_id
    ).all()

    candidates = []
    for center in centers:
        jurisdiction = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id == center.id, Jurisdiction.is_active == True
        ).first()
        if not jurisdiction or not jurisdiction.geometry or not jurisdiction.geometry.get("coordinates"):
            continue
        centroid = shape(jurisdiction.geometry).centroid
        distance = haversine_distance(lat, lon, centroid.y, centroid.x)
        candidates.append((center, distance))
    candidates.sort(key=lambda pair: pair[1])

    for center, _ in candidates:
        vehicle = db.query(Vehicle).filter(
            Vehicle.safety_center_id == center.id, Vehicle.vehicle_type == vehicle_type
        ).first()
        if not vehicle:
            continue
        active = _count_active_assignments(db, vehicle_type, center.id, None)
        if vehicle.count - active <= 0:
            continue
        return IncidentVehicleAssignment(
            incident_id=incident.id,
            vehicle_type=vehicle_type,
            unit_role=DispatchRole.firefighter,
            unit_name=f"{center.station_name}(지원)",
            required_crew=VEHICLE_CREW_SIZE[vehicle_type],
            safety_center_id=center.id,
            rescue_unit_id=None,
        )
    return None

def get_extra_vehicle_types(db: Session, incident: Incident) -> set[VehicleType]:
    """주변 위험요소·취약시설에 따라 기본 배정에 추가할 차종. 안전센터 소속 신고에만 적용
    (구조대는 소방서당 1개뿐이라 화학차/구급차 자체 재고가 없어 대상 아님)."""
    extra = set()
    if incident.latitude is None or incident.longitude is None:
        return extra

    lat, lon = float(incident.latitude), float(incident.longitude)

    if get_nearby_hazmat_facilities(db, lat, lon, radius_km=NEARBY_RADIUS_M / 1000):
        extra.add(VehicleType.화학차)
    if count_nearby_category("OL7", lat, lon, NEARBY_RADIUS_M) > 0:
        extra.add(VehicleType.화학차)

    if count_nearby_category("SC4", lat, lon, NEARBY_RADIUS_M) > 0:
        extra.add(VehicleType.구급차)
    if count_nearby_category("PS3", lat, lon, NEARBY_RADIUS_M) > 0:
        extra.add(VehicleType.구급차)

    return extra

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

    if not is_rescue:
        extra_types = get_extra_vehicle_types(db, incident)
        needed_types = needed_types + [t for t in extra_types if t not in needed_types]

    unit_filter = Vehicle.rescue_unit_id == unit.id if is_rescue else Vehicle.safety_center_id == unit.id
    vehicles = db.query(Vehicle).filter(unit_filter, Vehicle.vehicle_type.in_(needed_types)).all()
    vehicles_by_type = {v.vehicle_type: v for v in vehicles}

    assignments = []
    for vehicle_type in needed_types:
        vehicle = vehicles_by_type.get(vehicle_type)
        available = 0
        if vehicle:
            active = _count_active_assignments(db, vehicle_type, safety_center_id, rescue_unit_id)
            available = max(0, vehicle.count - active)

        for _ in range(available):
            assignment = IncidentVehicleAssignment(
                incident_id=incident.id,
                vehicle_type=vehicle_type,
                unit_role=unit_role,
                unit_name=unit.station_name,
                required_crew=VEHICLE_CREW_SIZE[vehicle_type],
                safety_center_id=safety_center_id,
                rescue_unit_id=rescue_unit_id,
            )
            db.add(assignment)
            assignments.append(assignment)

        if available == 0 and not is_rescue:
            borrowed = _borrow_from_nearby_centers(db, incident, station_id, vehicle_type, unit.id)
            if borrowed:
                db.add(borrowed)
                assignments.append(borrowed)

    return assignments
