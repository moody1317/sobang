from datetime import datetime
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentStatus
from app.models.incident_dispatch import IncidentDispatch, DispatchRole
from app.models.incident_vehicle_assignment import IncidentVehicleAssignment
from app.models.user import User, UnitType

def infer_unit_role(user: User) -> DispatchRole:
    return DispatchRole.rescuer if user.unit_type == UnitType.RESCUE_SQUAD else DispatchRole.firefighter

def get_dispatch_summary(db: Session, incident: Incident) -> dict:
    required_crew = (
        db.query(IncidentVehicleAssignment.unit_role, IncidentVehicleAssignment.required_crew)
        .filter(IncidentVehicleAssignment.incident_id == incident.id)
        .all()
    )
    required_firefighter_count = sum(c for role, c in required_crew if role == DispatchRole.firefighter)
    required_rescuer_count = sum(c for role, c in required_crew if role == DispatchRole.rescuer)

    roles = [
        role for (role,) in
        db.query(IncidentDispatch.unit_role).filter(IncidentDispatch.incident_id == incident.id).all()
    ]
    assigned_firefighter_count = roles.count(DispatchRole.firefighter)
    assigned_rescuer_count = roles.count(DispatchRole.rescuer)

    return {
        "required_firefighter_count": required_firefighter_count,
        "required_rescuer_count": required_rescuer_count,
        "assigned_firefighter_count": assigned_firefighter_count,
        "assigned_rescuer_count": assigned_rescuer_count,
        "is_fully_dispatched": (
            assigned_firefighter_count >= required_firefighter_count
            and assigned_rescuer_count >= required_rescuer_count
        ),
    }

def confirm_dispatch(db: Session, incident: Incident, user: User) -> IncidentDispatch:
    existing = (
        db.query(IncidentDispatch)
        .filter(IncidentDispatch.incident_id == incident.id, IncidentDispatch.user_id == user.id)
        .first()
    )
    if existing:
        raise ValueError("이미 이 사건에 출동 등록되어 있습니다.")

    role = infer_unit_role(user)
    summary = get_dispatch_summary(db, incident)
    if role == DispatchRole.firefighter:
        if summary["required_firefighter_count"] == 0:
            raise ValueError("이 사건에는 소방관 배정이 필요하지 않습니다.")
        if summary["assigned_firefighter_count"] >= summary["required_firefighter_count"]:
            raise ValueError("소방관 출동 정원이 이미 찼습니다.")
    else:
        if summary["required_rescuer_count"] == 0:
            raise ValueError("이 사건에는 구급/구조 인력 배정이 필요하지 않습니다.")
        if summary["assigned_rescuer_count"] >= summary["required_rescuer_count"]:
            raise ValueError("구급대원 출동 정원이 이미 찼습니다.")

    dispatch = IncidentDispatch(incident_id=incident.id, user_id=user.id, unit_role=role)
    db.add(dispatch)
    db.flush()

    updated_summary = get_dispatch_summary(db, incident)
    if updated_summary["is_fully_dispatched"] and incident.status == IncidentStatus.신고접수:
        incident.status = IncidentStatus.출동중
        incident.dispatched_at = datetime.now()

    db.commit()
    db.refresh(dispatch)
    return dispatch

def get_dispatch_dates(db: Session, user_id: int, year: int, month: int) -> list:
    rows = (
        db.query(IncidentDispatch.dispatched_at)
        .filter(
            IncidentDispatch.user_id == user_id,
            extract("year", IncidentDispatch.dispatched_at) == year,
            extract("month", IncidentDispatch.dispatched_at) == month,
        )
        .all()
    )
    return sorted({dispatched_at.date() for (dispatched_at,) in rows})

def complete_return(db: Session, incident: Incident, user: User, activity_note: str, equipment_used: str | None) -> IncidentDispatch:
    dispatch = (
        db.query(IncidentDispatch)
        .filter(IncidentDispatch.incident_id == incident.id, IncidentDispatch.user_id == user.id)
        .first()
    )
    if not dispatch:
        raise ValueError("이 사건에 대한 본인의 출동 기록이 없습니다.")

    dispatch.returned_at = datetime.now()
    dispatch.activity_note = activity_note
    dispatch.equipment_used = equipment_used

    db.commit()
    db.refresh(dispatch)
    return dispatch
