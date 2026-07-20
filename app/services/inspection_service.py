from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.inspection import Inspection, InspectionStatus
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter
from app.models.local_unit import LocalUnit
from app.models.notification import Notification, NotificationLevel
from app.services.notification_service import create_notification

DEADLINE_DAYS = (7, 3, 0)

def _day_label(days_left: int) -> str:
    return "오늘" if days_left == 0 else f"{days_left}일 후"

def _resolve_jurisdiction_station_id(
    jurisdiction: Jurisdiction, safety_center_parent: dict, local_unit_parent: dict
) -> int | None:
    if jurisdiction.station_id:
        return jurisdiction.station_id
    if jurisdiction.safety_center_id:
        return safety_center_parent.get(jurisdiction.safety_center_id)
    if jurisdiction.local_unit_id:
        return local_unit_parent.get(jurisdiction.local_unit_id)
    return None

def _already_sent(db: Session, title: str, message: str) -> bool:
    today_start = datetime.combine(date.today(), datetime.min.time())
    return db.query(Notification).filter(
        Notification.title == title,
        Notification.message == message,
        Notification.created_at >= today_start,
    ).first() is not None

def _notify_deadline(
    db: Session, jurisdiction: Jurisdiction, station_id: int | None, target: str, deadline: date, days_left: int, label: str
) -> bool:
    title = jurisdiction.ward_name
    message = f"{target} {label} 기한이 {_day_label(days_left)}({deadline.isoformat()})입니다."
    if _already_sent(db, title, message):
        return False
    create_notification(
        db,
        level=NotificationLevel.WARNING if days_left == 0 else NotificationLevel.CAUTION,
        source="inspection",
        title=title,
        message=message,
        station_id=station_id,
    )
    return True

def check_inspection_deadlines(db: Session) -> dict:
    today = date.today()
    jurisdiction_by_id = {j.id: j for j in db.query(Jurisdiction).all()}
    safety_center_parent = {c.id: c.parent_station_id for c in db.query(SafetyCenter).all()}
    local_unit_parent = {u.id: u.parent_station_id for u in db.query(LocalUnit).all()}
    created = 0

    scheduled = db.query(Inspection).filter(Inspection.status == InspectionStatus.예정).all()
    for insp in scheduled:
        jurisdiction = jurisdiction_by_id.get(insp.jurisdiction_id)
        if not jurisdiction:
            continue
        days_left = (insp.scheduled_date - today).days
        if days_left in DEADLINE_DAYS:
            station_id = _resolve_jurisdiction_station_id(jurisdiction, safety_center_parent, local_unit_parent)
            if _notify_deadline(db, jurisdiction, station_id, insp.target, insp.scheduled_date, days_left, "점검 예정"):
                created += 1

    completed_with_next = (
        db.query(Inspection)
        .filter(Inspection.status == InspectionStatus.완료, Inspection.next_inspection_date.isnot(None))
        .all()
    )
    for insp in completed_with_next:
        jurisdiction = jurisdiction_by_id.get(insp.jurisdiction_id)
        if not jurisdiction:
            continue
        days_left = (insp.next_inspection_date - today).days
        if days_left in DEADLINE_DAYS:
            station_id = _resolve_jurisdiction_station_id(jurisdiction, safety_center_parent, local_unit_parent)
            if _notify_deadline(db, jurisdiction, station_id, insp.target, insp.next_inspection_date, days_left, "재점검"):
                created += 1

    return {
        "created": created,
        "checked_scheduled": len(scheduled),
        "checked_recheck": len(completed_with_next),
    }
