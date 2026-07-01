import random
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.notification import Notification, NotificationLevel

DONG_POOL = ["중앙동", "탑대성동", "미원면", "금천동", "산남동", "복대동", "용암동", "오송읍"]

DESCRIPTION_MAP = {
    IncidentType.FIRE: "건물 화재 신고가 접수되었습니다.",
    IncidentType.RESCUE: "구조 요청이 접수되었습니다.",
    IncidentType.EMERGENCY: "구급 출동 요청이 접수되었습니다.",
    IncidentType.HAZMAT: "위험물 누출 신고가 접수되었습니다.",
    IncidentType.OTHER: "기타 신고가 접수되었습니다.",
}

LEVEL_MAP = {
    IncidentType.FIRE: NotificationLevel.DANGER,
    IncidentType.HAZMAT: NotificationLevel.DANGER,
    IncidentType.RESCUE: NotificationLevel.WARNING,
    IncidentType.EMERGENCY: NotificationLevel.WARNING,
    IncidentType.OTHER: NotificationLevel.CAUTION,
}


def simulate_incident(db: Session, station_id: int | None = None) -> tuple[Incident, Notification]:
    """데모/대회용 가상 신고 생성. 실제 119 연동 전까지 사용."""
    incident_type = random.choice(list(IncidentType))
    dong_name = random.choice(DONG_POOL)

    incident = Incident(
        incident_type=incident_type,
        status=IncidentStatus.REPORTED,
        dong_name=dong_name,
        address=f"충북 청주시 {dong_name} 일대",
        station_id=station_id,
        description=DESCRIPTION_MAP[incident_type],
        is_simulated="Y",
    )
    db.add(incident)
    db.flush()  # incident.id 확보

    notification = Notification(
        level=LEVEL_MAP[incident_type],
        title=dong_name,
        message=f"{incident_type.value} 신고가 접수되어 출동이 시작됩니다.",
        source="incident",
        related_incident_id=incident.id,
        station_id=station_id,
    )
    db.add(notification)

    db.commit()
    db.refresh(incident)
    db.refresh(notification)

    return incident, notification