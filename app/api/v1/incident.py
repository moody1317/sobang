from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db_session
from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.notification import NotificationLevel
from app.services.incident_service import simulate_incident as simulate_incident_service
from app.services.notification_service import create_notification

router = APIRouter(prefix="/incidents", tags=["incidents"])

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
    return {
        "incident_id": incident.id,
        "incident_type": incident.incident_type.value,
        "status": incident.status.value,
        "dong_name": incident.dong_name,
        "safety_center_id": incident.safety_center_id,
        "notification_id": notification.id,
    }

@router.patch("/{incident_id}/status")
def update_incident_status(incident_id: int, new_status: IncidentStatus, db: Session = Depends(get_db_session)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return {"error": "not found"}

    incident.status = new_status
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
            message=f"{incident.incident_type.value} 상황이 종료되었습니다.",
            station_id=incident.station_id,
            related_incident_id=incident.id,
        )

    db.commit()
    return {"incident_id": incident.id, "status": incident.status.value}

@router.get("/active")
def list_active_incidents(db: Session = Depends(get_db_session)):
    """진행 중(종료 아닌) 사건 목록 — 위험 스코어 가산점 계산에 사용"""
    items = db.query(Incident).filter(Incident.status != IncidentStatus.종료).all()
    return [
        {
            "id": i.id,
            "incident_type": i.incident_type.value,
            "status": i.status.value,
            "station_id": i.station_id,
            "safety_center_id": i.safety_center_id,
            "dong_name": i.dong_name,
            "reported_at": i.reported_at.isoformat(),
        }
        for i in items
    ]