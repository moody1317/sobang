from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.services.incident_service import simulate_incident
from app.models.user import User

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/simulate")
def simulate(
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    incident, notification = simulate_incident(db, station_id=admin_user.station_id)
    return {
        "message": "가상 신고가 생성되었습니다.",
        "incident_id": incident.id,
        "notification_id": notification.id,
        "title": notification.title,
        "message_text": notification.message,
        "level": notification.level.value,
    }