import random
import math
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.notification import Notification, NotificationLevel
from app.models.safety_center import SafetyCenter
from app.models.jurisdiction import Jurisdiction

DONG_POOL = ["중앙동", "탑대성동", "미원면", "금천동", "산남동", "복대동", "용암동", "오송읍"]

DESCRIPTION_MAP = {
    IncidentType.화재: "건물 화재 신고가 접수되었습니다.",
    IncidentType.구조: "구조 요청이 접수되었습니다.",
    IncidentType.구급: "구급 출동 요청이 접수되었습니다.",
    IncidentType.위험물: "위험물 누출 신고가 접수되었습니다.",
    IncidentType.기타: "기타 신고가 접수되었습니다.",
}

LEVEL_MAP = {
    IncidentType.화재: NotificationLevel.DANGER,
    IncidentType.위험물: NotificationLevel.DANGER,
    IncidentType.구조: NotificationLevel.WARNING,
    IncidentType.구급: NotificationLevel.WARNING,
    IncidentType.기타: NotificationLevel.CAUTION,
}


def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_safety_center(db: Session, station_id: int, lat: float, lon: float):
    from shapely.geometry import shape

    centers = db.query(SafetyCenter).filter(SafetyCenter.parent_station_id == station_id).all()
    candidates = []
    for center in centers:
        jurisdiction = (
            db.query(Jurisdiction)
            .filter(Jurisdiction.safety_center_id == center.id, Jurisdiction.is_active == True)
            .first()
        )
        if not jurisdiction:
            continue
        if not jurisdiction.geometry or not jurisdiction.geometry.get("coordinates"):
            continue  # geometry 누락/빈 값 — 거리 계산 불가하니 후보에서 제외 (500 방지)
        centroid = shape(jurisdiction.geometry).centroid
        distance = haversine_distance(lat, lon, centroid.y, centroid.x)
        candidates.append((center, distance))

    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[1])
    return candidates[0]


def simulate_incident(
    db: Session,
    station_id: int | None = None,
    incident_type: IncidentType | None = None,
    dong_name: str | None = None,
    address: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    description: str | None = None,
    fire_truck_count: int = 0,
    ambulance_count: int = 0,
) -> tuple[Incident, Notification]:
    incident_type = incident_type or random.choice(list(IncidentType))
    dong_name = dong_name or random.choice(DONG_POOL)
    address = address or f"충북 청주시 {dong_name} 일대"
    description = description or DESCRIPTION_MAP[incident_type]

    safety_center_id = None
    center_name = None
    if station_id and latitude is not None and longitude is not None:
        nearest_center, _ = find_nearest_safety_center(db, station_id, latitude, longitude)
        if nearest_center:
            safety_center_id = nearest_center.id
            center_name = nearest_center.station_name

    incident = Incident(
        incident_type=incident_type,
        status=IncidentStatus.신고접수,
        dong_name=dong_name,
        address=address,
        station_id=station_id,
        safety_center_id=safety_center_id,
        latitude=str(latitude) if latitude is not None else None,
        longitude=str(longitude) if longitude is not None else None,
        description=description,
        is_simulated="Y",
        fire_truck_count=fire_truck_count,
        ambulance_count=ambulance_count,
    )
    db.add(incident)
    db.flush()

    notification = Notification(
        level=LEVEL_MAP[incident_type],
        title=center_name or dong_name,
        message=f"{incident_type.value} 신고가 접수되어 {center_name or '관할 소방서'} 출동이 시작됩니다.",
        source="incident",
        related_incident_id=incident.id,
        station_id=station_id,
    )
    db.add(notification)

    db.commit()
    db.refresh(incident)
    db.refresh(notification)

    return incident, notification