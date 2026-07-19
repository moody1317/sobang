import requests
from datetime import datetime, timedelta
from shapely.geometry import shape
from sqlalchemy.orm import Session
from app.models.active_risk_event import ActiveRiskEvent
from app.core.config import settings
from app.services.notification_service import create_notification
from app.services.incident_service import haversine_distance
from app.models.notification import NotificationLevel

DECAY_WINDOW_HOURS = 72

BASE_BOOST_BY_MAGNITUDE = [
    (5.0, 30),
    (4.0, 15),
    (3.0, 5),
]

def fetch_earthquakes_raw(page_no: int = 1, num_of_rows: int = 10, from_tm_fc: str = None, to_tm_fc: str = None) -> dict:
    params = {
        "ServiceKey": settings.EARTHQUAKE_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": "JSON",
    }
    if from_tm_fc:
        params["fromTmFc"] = from_tm_fc
    if to_tm_fc:
        params["toTmFc"] = to_tm_fc

    response = requests.get(settings.EARTHQUAKE_API_BASE_URL, params=params, timeout=10)
    print("상태코드:", response.status_code)
    print("응답 본문:", response.text[:1000])
    response.raise_for_status()
    return response.json()

def fetch_earthquakes_preview(num_of_rows: int = 5) -> dict:
    return fetch_earthquakes_raw(num_of_rows=num_of_rows)

def get_base_boost(magnitude: float) -> float:
    for threshold, boost in BASE_BOOST_BY_MAGNITUDE:
        if magnitude >= threshold:
            return boost
    return 0

def get_affected_radius_km(magnitude: float) -> float:
    if magnitude < 3.0:
        return 0
    elif magnitude < 4.0:
        return 20
    elif magnitude < 5.0:
        return 50
    else:
        return 100
    
def parse_tm(tm_str: str) -> datetime:
    return datetime.strptime(str(tm_str), "%Y%m%d%H%M%S")

def register_earthquake_event(db: Session, eqk_data: dict):
    magnitude = float(eqk_data.get("mt", 0) or 0)
    if magnitude < 3.0:
        return None

    occurred_at = parse_tm(eqk_data["tmEqk"])

    event = ActiveRiskEvent(
        event_type="지진",
        epicenter_lat=eqk_data.get("lat"),
        epicenter_lon=eqk_data.get("lon"),
        magnitude=magnitude,
        affected_radius_km=get_affected_radius_km(magnitude),
        occurred_at=occurred_at,
        expires_at=occurred_at + timedelta(hours=DECAY_WINDOW_HOURS),
    )
    db.add(event)
    db.commit()

    level = NotificationLevel.DANGER if magnitude >= 5.0 else NotificationLevel.WARNING
    create_notification(
        db,
        level=level,
        source="earthquake",
        title="관할 전역",
        message=f"규모 {magnitude} 지진 발생 — {eqk_data.get('loc', '위치 미상')}",
        station_id=None,
    )
    
    return event

def is_domestic_earthquake(eqk_data: dict) -> bool:
    rem = eqk_data.get("rem", "") or ""
    if "국내영향없음" in rem:
        return False

    lat = float(eqk_data.get("lat", 0) or 0)
    lon = float(eqk_data.get("lon", 0) or 0)
    return 33.0 <= lat <= 43.0 and 124.0 <= lon <= 132.0

def get_earthquake_boost_for_jurisdiction(db: Session, jurisdiction, now: datetime = None) -> float:
    now = now or datetime.now()
    if not jurisdiction.geometry:
        return 0.0

    active_events = db.query(ActiveRiskEvent).filter(
        ActiveRiskEvent.event_type == "지진",
        ActiveRiskEvent.expires_at > now,
    ).all()
    if not active_events:
        return 0.0

    centroid = shape(jurisdiction.geometry).centroid
    total = 0.0
    for event in active_events:
        distance = haversine_distance(centroid.y, centroid.x, float(event.epicenter_lat), float(event.epicenter_lon))
        radius = float(event.affected_radius_km)
        space_decay = max(0.0, 1 - distance / radius) if radius else 0.0
        elapsed_hours = (now - event.occurred_at).total_seconds() / 3600
        time_decay = max(0.0, 1 - elapsed_hours / DECAY_WINDOW_HOURS)
        total += get_base_boost(float(event.magnitude)) * space_decay * time_decay

    return round(total, 2)


def poll_recent_earthquakes(db: Session):
    today = datetime.now().strftime("%Y%m%d")
    three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")

    raw = fetch_earthquakes_raw(num_of_rows=100, from_tm_fc=three_days_ago, to_tm_fc=today)
    items = raw.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]

    created, skipped_foreign = 0, 0

    for eqk in items:
        if not is_domestic_earthquake(eqk):
            skipped_foreign += 1
            continue

        exists = db.query(ActiveRiskEvent).filter(
            ActiveRiskEvent.event_type == "지진",
            ActiveRiskEvent.occurred_at == parse_tm(eqk.get("tmEqk")),
        ).first()
        if exists:
            continue

        event = register_earthquake_event(db, eqk)
        if event:
            created += 1

    return {"checked": len(items), "created": created, "skipped_foreign": skipped_foreign}