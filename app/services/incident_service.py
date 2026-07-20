import random
import math
import re
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentType, IncidentStatus
from app.models.notification import Notification, NotificationLevel
from app.models.safety_center import SafetyCenter
from app.models.jurisdiction import Jurisdiction
from app.models.jurisdiction_dong import JurisdictionDong
from app.services.vehicle_dispatch_service import assign_vehicles_for_incident

DONG_POOL = ["중앙동", "탑대성동", "미원면", "금천동", "산남동", "복대1동", "용암1동", "오송읍"]

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
    from shapely.geometry import shape, Point

    centers = db.query(SafetyCenter).filter(SafetyCenter.parent_station_id == station_id).all()
    point = Point(lon, lat)

    candidates = []
    containing = []
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
        polygon = shape(jurisdiction.geometry)
        centroid = polygon.centroid
        distance = haversine_distance(lat, lon, centroid.y, centroid.x)
        candidates.append((center, distance))
        if polygon.contains(point):
            containing.append((center, distance))

    # 실제로 이 좌표를 포함하는 관할구역이 있으면 그걸 우선 (중심점 거리는 폴리곤 모양에 따라
    # 실제 소속과 어긋날 수 있음 — 여러 개 겹치면 중심점이 더 가까운 쪽)
    if containing:
        containing.sort(key=lambda x: x[1])
        return containing[0]

    if not candidates:
        return None, None
    candidates.sort(key=lambda x: x[1])
    return candidates[0]


def find_safety_center_by_dong_name(db: Session, station_id: int, dong_name: str):
    centers = db.query(SafetyCenter).filter(SafetyCenter.parent_station_id == station_id).all()
    center_by_id = {c.id: c for c in centers}
    if not center_by_id:
        return None

    jurisdictions = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.safety_center_id.in_(center_by_id.keys()), Jurisdiction.is_active == True)
        .all()
    )
    jurisdiction_ids = [j.id for j in jurisdictions]
    if not jurisdiction_ids:
        return None

    matched = (
        db.query(JurisdictionDong)
        .filter(JurisdictionDong.jurisdiction_id.in_(jurisdiction_ids), JurisdictionDong.dong_nm == dong_name)
        .first()
    )
    if not matched:
        # "복대동"처럼 실제로는 "복대1동"/"복대2동"으로 나뉜 동은 접미사를 떼고 접두어로 재시도
        prefix = re.sub(r"(동|읍|면)$", "", dong_name)
        matched = (
            db.query(JurisdictionDong)
            .filter(JurisdictionDong.jurisdiction_id.in_(jurisdiction_ids), JurisdictionDong.dong_nm.like(f"{prefix}%"))
            .first()
        )
    if not matched:
        return None

    jurisdiction = next((j for j in jurisdictions if j.id == matched.jurisdiction_id), None)
    if not jurisdiction:
        return None
    return center_by_id.get(jurisdiction.safety_center_id)


def simulate_incident(
    db: Session,
    station_id: int | None = None,
    incident_type: IncidentType | None = None,
    dong_name: str | None = None,
    address: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    description: str | None = None,
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

    if not safety_center_id and station_id:
        center = find_safety_center_by_dong_name(db, station_id, dong_name)
        if center:
            safety_center_id = center.id
            center_name = center.station_name

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
    )
    db.add(incident)
    db.flush()

    if station_id:
        assign_vehicles_for_incident(db, incident, station_id)

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