from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db_session, get_current_active_user
from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.incident_dispatch import IncidentDispatch
from app.models.notification import NotificationLevel
from app.models.user import User
from app.schemas.incident import IncidentReturnRequest
from app.services.incident_service import simulate_incident as simulate_incident_service
from app.services.notification_service import create_notification
from app.services.risk_score_service import recalculate_active_incident_boost
from app.services import incident_dispatch_service
from app.services import vehicle_dispatch_service

router = APIRouter(prefix="/incidents", tags=["incidents"])

def _get_incident_or_404(db: Session, incident_id: int) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사건을 찾을 수 없습니다.")
    return incident

@router.post("/simulate")
def simulate_incident(
    station_id: int = None,
    incident_type: IncidentType = None,
    dong_name: str = None,
    address: str = None,
    latitude: float = None,
    longitude: float = None,
    description: str = None,
    db: Session = Depends(get_db_session),
):
    incident, notification = simulate_incident_service(
        db,
        station_id=station_id,
        incident_type=incident_type,
        dong_name=dong_name,
        address=address,
        latitude=latitude,
        longitude=longitude,
        description=description,
    )
    recalculate_active_incident_boost(db, incident)
    return {
        "incident_id": incident.id,
        "incident_type": incident.incident_type.value,
        "status": incident.status.value,
        "dong_name": incident.dong_name,
        "safety_center_id": incident.safety_center_id,
        "notification_id": notification.id,
        **incident_dispatch_service.get_dispatch_summary(db, incident),
    }

@router.patch("/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    new_status: IncidentStatus,
    is_false_alarm: bool = None,
    db: Session = Depends(get_db_session),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "not found"}

    incident.status = new_status
    if is_false_alarm is not None:
        incident.is_false_alarm = is_false_alarm
    now = datetime.now()

    if new_status == IncidentStatus.출동중:
        incident.dispatched_at = now
    elif new_status == IncidentStatus.종료:
        incident.resolved_at = now
        create_notification(
            db,
            level=NotificationLevel.SAFE,
            source="incident",
            title=incident.dong_name,
            message=(
                "허위 신고로 확인되어 종료되었습니다." if incident.is_false_alarm
                else f"{incident.incident_type.value} 상황이 종료되었습니다."
            ),
            station_id=incident.station_id,
            related_incident_id=incident.id,
        )

    db.commit()
    # 종료/허위신고 처리 모두 여기서 처리 — get_active_incidents_for_safety_center의
    # 조회 조건(status != 종료 AND is_false_alarm != True)에서 자동으로 빠지므로 가산점이 내려간다.
    recalculate_active_incident_boost(db, incident)
    return {"incident_id": incident.id, "status": incident.status.value, "is_false_alarm": incident.is_false_alarm}

@router.get("/active")
def list_active_incidents(db: Session = Depends(get_db_session)):
    """진행 중(종료 아니고 허위신고 아닌) 사건 목록 — 위험 스코어 가산점 계산에 사용"""
    items = (
        db.query(Incident)
        .filter(Incident.status != IncidentStatus.종료, Incident.is_false_alarm == False)  # noqa: E712
        .all()
    )
    return [
        {
            "id": i.id,
            "incident_type": i.incident_type.value,
            "status": i.status.value,
            "station_id": i.station_id,
            "safety_center_id": i.safety_center_id,
            "dong_name": i.dong_name,
            "address": i.address,
            "latitude": float(i.latitude) if i.latitude is not None else None,
            "longitude": float(i.longitude) if i.longitude is not None else None,
            "description": i.description,
            "reported_at": i.reported_at.isoformat(),
            "vehicles": vehicle_dispatch_service.get_vehicle_assignments(db, i.id),
            **incident_dispatch_service.get_dispatch_summary(db, i),
        }
        for i in items
    ]

@router.post("/{incident_id}/dispatch")
def confirm_dispatch(
    incident_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    incident = _get_incident_or_404(db, incident_id)

    try:
        dispatch = incident_dispatch_service.confirm_dispatch(db, incident, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "dispatch_id": dispatch.id,
        "incident_id": incident.id,
        "unit_role": dispatch.unit_role.value,
        "dispatched_at": dispatch.dispatched_at.isoformat(),
        **incident_dispatch_service.get_dispatch_summary(db, incident),
    }

@router.get("/{incident_id}/dispatches")
def list_incident_dispatches(incident_id: int, db: Session = Depends(get_db_session)):
    """사건에 출동 등록된 인원 목록 — 여러 명이 출동할 때 누가 가는지 확인용"""
    rows = (
        db.query(IncidentDispatch, User)
        .join(User, IncidentDispatch.user_id == User.id)
        .filter(IncidentDispatch.incident_id == incident_id)
        .all()
    )
    return [
        {
            "dispatch_id": dispatch.id,
            "user_id": user.id,
            "name": user.name,
            "unit_role": dispatch.unit_role.value,
            "dispatched_at": dispatch.dispatched_at.isoformat(),
            "returned_at": dispatch.returned_at.isoformat() if dispatch.returned_at else None,
        }
        for dispatch, user in rows
    ]

@router.get("/{incident_id}/vehicles")
def list_incident_vehicles(incident_id: int, db: Session = Depends(get_db_session)):
    """이 사건에 자동 배정된 차량 목록"""
    return vehicle_dispatch_service.get_vehicle_assignments(db, incident_id)

@router.get("/dispatches/my")
def list_my_dispatch_dates(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """일정 페이지 달력에 출동 표시를 하기 위한, 이번 달 본인 출동 날짜 목록"""
    dates = incident_dispatch_service.get_dispatch_dates(db, current_user.id, year, month)
    return [d.isoformat() for d in dates]

@router.patch("/{incident_id}/dispatch/return")
def return_from_dispatch(
    incident_id: int,
    data: IncidentReturnRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    incident = _get_incident_or_404(db, incident_id)

    try:
        dispatch = incident_dispatch_service.complete_return(
            db, incident, current_user, data.activity_note, data.equipment_used
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "dispatch_id": dispatch.id,
        "incident_id": incident.id,
        "returned_at": dispatch.returned_at.isoformat(),
        "activity_note": dispatch.activity_note,
        "equipment_used": dispatch.equipment_used,
    }