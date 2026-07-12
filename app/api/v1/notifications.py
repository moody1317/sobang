from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.api.deps import get_db_session, get_current_active_user
from app.models.notification import Notification
from app.models.user import User, UnitType
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu, extract_city_name

router = APIRouter(prefix="/notifications", tags=["notifications"])

def get_my_sigungu_set(db: Session, current_user: User) -> set:
    if current_user.unit_type == UnitType.SAFETY_CENTER and current_user.safety_center_id:
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id == current_user.safety_center_id, Jurisdiction.is_active == True
        ).all()
    else:
        center_ids = [
            c.id for c in db.query(SafetyCenter)
            .filter(SafetyCenter.parent_station_id == current_user.station_id)
            .all()
        ]
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id.in_(center_ids), Jurisdiction.is_active == True
        ).all()

    sigungu_set = {get_jurisdiction_sigungu(db, j) for j in jurisdictions}
    sigungu_set.discard(None)
    return {extract_city_name(s) for s in sigungu_set}

@router.get("")
def list_notifications(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    my_sigungu = get_my_sigungu_set(db, current_user)

    query = db.query(Notification).filter(
        or_(
            Notification.station_id == current_user.station_id,
            Notification.title == "관할 전역",
            Notification.title.in_(my_sigungu) if my_sigungu else False,
        )
    )
    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()
    items = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()

    return {
        "items": [
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
        ],
        "total": total,
    }

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    my_sigungu = get_my_sigungu_set(db, current_user)
    count = db.query(Notification).filter(
        Notification.is_read == False,
        or_(
            Notification.station_id == current_user.station_id,
            Notification.title == "관할 전역",
            Notification.title.in_(my_sigungu) if my_sigungu else False,
        ),
    ).count()
    return {"unread_count": count}

@router.patch("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db_session)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return {"error": "not found"}
    notif.is_read = True
    db.commit()
    return {"success": True}