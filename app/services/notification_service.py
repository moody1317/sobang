from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationLevel

def create_notification(
    db: Session,
    level: NotificationLevel,
    source: str,
    title: str,
    message: str,
    station_id: int = None,
    related_incident_id: int = None,
) -> Notification:
    notif = Notification(
        level=level,
        source=source,
        title=title,
        message=message,
        station_id=station_id,
        related_incident_id=related_incident_id,
    )
    db.add(notif)
    db.commit()
    return notif