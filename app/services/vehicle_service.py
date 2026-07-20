from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.rescue_unit import RescueUnit
from app.models.safety_center import SafetyCenter
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate

def _resolve_unit_station_id(db: Session, safety_center_id: int | None, rescue_unit_id: int | None) -> int | None:
    if safety_center_id is not None:
        unit = db.query(SafetyCenter).filter(SafetyCenter.id == safety_center_id).first()
        return unit.parent_station_id if unit else None
    if rescue_unit_id is not None:
        unit = db.query(RescueUnit).filter(RescueUnit.id == rescue_unit_id).first()
        return unit.parent_station_id if unit else None
    return None

def get_vehicles_for_station(db: Session, station_id: int) -> list[dict]:
    centers = db.query(SafetyCenter).filter(SafetyCenter.parent_station_id == station_id).all()
    rescue_units = db.query(RescueUnit).filter(RescueUnit.parent_station_id == station_id).all()
    center_ids = [c.id for c in centers]
    rescue_ids = [r.id for r in rescue_units]
    unit_names = {("safety_center", c.id): c.station_name for c in centers}
    unit_names.update({("rescue_unit", r.id): r.station_name for r in rescue_units})

    if not center_ids and not rescue_ids:
        return []

    vehicles = (
        db.query(Vehicle)
        .filter(or_(Vehicle.safety_center_id.in_(center_ids), Vehicle.rescue_unit_id.in_(rescue_ids)))
        .all()
    )

    return [
        {
            "id": v.id,
            "vehicle_type": v.vehicle_type.value,
            "count": v.count,
            "safety_center_id": v.safety_center_id,
            "rescue_unit_id": v.rescue_unit_id,
            "unit_name": (
                unit_names.get(("safety_center", v.safety_center_id))
                or unit_names.get(("rescue_unit", v.rescue_unit_id))
            ),
        }
        for v in vehicles
    ]

def create_vehicle(db: Session, admin_station_id: int, data: VehicleCreate) -> Vehicle:
    if (data.safety_center_id is None) == (data.rescue_unit_id is None):
        raise ValueError("안전센터 또는 구조대 중 하나만 선택해야 합니다.")

    unit_station_id = _resolve_unit_station_id(db, data.safety_center_id, data.rescue_unit_id)
    if unit_station_id != admin_station_id:
        raise ValueError("소속 소방서의 시설만 등록할 수 있습니다.")

    vehicle = Vehicle(
        vehicle_type=data.vehicle_type,
        count=data.count,
        safety_center_id=data.safety_center_id,
        rescue_unit_id=data.rescue_unit_id,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def _get_owned_vehicle(db: Session, admin_station_id: int, vehicle_id: int) -> Vehicle:
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise ValueError("차량 정보를 찾을 수 없습니다.")
    unit_station_id = _resolve_unit_station_id(db, vehicle.safety_center_id, vehicle.rescue_unit_id)
    if unit_station_id != admin_station_id:
        raise ValueError("소속 소방서의 차량만 관리할 수 있습니다.")
    return vehicle

def update_vehicle_count(db: Session, admin_station_id: int, vehicle_id: int, count: int) -> Vehicle:
    vehicle = _get_owned_vehicle(db, admin_station_id, vehicle_id)
    vehicle.count = count
    db.commit()
    db.refresh(vehicle)
    return vehicle

def delete_vehicle(db: Session, admin_station_id: int, vehicle_id: int) -> None:
    vehicle = _get_owned_vehicle(db, admin_station_id, vehicle_id)
    db.delete(vehicle)
    db.commit()
