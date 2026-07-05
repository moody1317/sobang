from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db_session
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    limit: int = Query(20, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db_session),
):
    query = db.query(Notification)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    items = query.order_by(desc(Notification.created_at)).limit(limit).all()

    return [
        {
            "id": n.id,
            "level": n.level.value,
            "source": n.source,
            "title": n.title,
            "message": n.message,
            "station_id": n.station_id,
            "related_incident_id": n.related_incident_id,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in items
    ]


@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db_session)):
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db_session)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return {"error": "not found"}
    notif.is_read = True
    db.commit()
    return {"success": True}