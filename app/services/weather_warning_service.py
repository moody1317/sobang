import json
import requests
from pathlib import Path
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.weather_warning import WeatherWarning
from app.models.station import Station
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu, extract_sigungu
from app.services.notification_service import create_notification
from app.models.notification import NotificationLevel
from datetime import datetime

WEATHER_STATION_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "weather_station_codes.json"
with open(WEATHER_STATION_CODES_PATH, encoding="utf-8") as f:
    WEATHER_STATIONS = json.load(f)

WEATHER_HIERARCHY_PATH = Path(__file__).resolve().parent.parent / "data" / "weather_area_hierarchy.json"
with open(WEATHER_HIERARCHY_PATH, encoding="utf-8") as f:
    WEATHER_HIERARCHY = json.load(f)

WARNING_TYPE_MAP = {
    1: "강풍", 2: "호우", 3: "한파", 4: "건조", 5: "폭풍해일",
    6: "풍랑", 7: "태풍", 8: "대설", 9: "황사", 12: "폭염",
}

WARNING_IMPACT = {
    "화재": [1, 4, 7],
    "구급": [3, 9, 12, 7],
    "구조": [2, 5, 6, 8, 7],
}

def resolve_sigungu_name(area_code: str) -> str:
    entry = WEATHER_HIERARCHY.get(area_code)
    return entry["sigungu_name"] if entry else None

def get_station_ids_for_sigungu(db: Session, sigungu: str) -> list[int]:
    """해당 sigungu를 관할하는 소방서 station_id 목록. 못 찾으면 빈 리스트(호출부에서 전역 발송으로 폴백)."""
    if not sigungu:
        return []
    stations = db.query(Station).filter(Station.is_active == True).all()
    return [
        s.id for s in stations
        if extract_sigungu(s.address, fallback_name=s.station_name) == sigungu
    ]

def get_active_warnings_for_jurisdiction(db: Session, jurisdiction) -> list[WeatherWarning]:
    sigungu = get_jurisdiction_sigungu(db, jurisdiction)  # 이미 있는 함수
    if not sigungu:
        return []
    return db.query(WeatherWarning).filter(WeatherWarning.sigungu_name == sigungu).all()

def fetch_pwn_cd(stn_id: str, page_no: int = 1, num_of_rows: int = 300, area_code: str = None, warning_type: str = None, from_tm_fc: str = None, to_tm_fc: str = None) -> dict:
    params = {
        "ServiceKey": settings.WEATHER_WARNING_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": "JSON",
        "stnId": stn_id,
    }
    if area_code:
        params["areaCode"] = area_code
    if warning_type:
        params["warningType"] = warning_type
    if from_tm_fc:
        params["fromTmFc"] = from_tm_fc
    if to_tm_fc:
        params["toTmFc"] = to_tm_fc

    response = requests.get(settings.WEATHER_WARNING_API_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def sync_weather_warnings(db: Session) -> dict:
    result = fetch_pwn_cd(stn_id="108")
    items = result.get("response", {}).get("body", {}).get("items", {}).get("item", [])

    already_active_pairs = {
        (w.sigungu_name, w.warn_var)
        for w in db.query(WeatherWarning).filter(WeatherWarning.is_active == True).all()
    }
    notified_this_run = set()  

    created, newly_issued, newly_cancelled = 0, 0, 0

    for item in items:
        if item.get("cancel") == "1":
            continue

        area_code = item.get("areaCode")
        warn_var = item.get("warnVar")
        command = item.get("command")
        sigungu = resolve_sigungu_name(area_code)
        pair = (sigungu, warn_var)

        if command in (2, 8):
            existing = db.query(WeatherWarning).filter(
                WeatherWarning.area_code == area_code,
                WeatherWarning.warn_var == warn_var,
                WeatherWarning.is_active == True,
            ).first()
            if existing:
                existing.is_active = False
                existing.cancelled_at = datetime.now()
                newly_cancelled += 1
                if pair not in notified_this_run:
                    notified_this_run.add(pair)
                    create_notification(
                        db, level=NotificationLevel.SAFE, source="weather",
                        title=sigungu or item.get("areaName"),
                        message=f"{WARNING_TYPE_MAP.get(warn_var)}특보 해제",
                        station_id=None,
                    )
            continue

        existing = db.query(WeatherWarning).filter(
            WeatherWarning.area_code == area_code,
            WeatherWarning.warn_var == warn_var,
            WeatherWarning.is_active == True,
        ).first()

        if not existing:
            db.add(WeatherWarning(
                area_code=area_code, area_name=item.get("areaName"), sigungu_name=sigungu,
                warn_var=warn_var, warn_stress=item.get("warnStress"), command=command,
                cancel=item.get("cancel"), tm_fc=str(item.get("tmFc")),
                start_time=str(item.get("startTime")), end_time=str(item.get("endTime")),
                is_active=True,
            ))
            created += 1

            if pair not in already_active_pairs and pair not in notified_this_run:
                notified_this_run.add(pair)
                newly_issued += 1
                create_notification(
                    db, level=NotificationLevel.ALERT, source="weather",
                    title=sigungu or item.get("areaName"),
                    message=f"{WARNING_TYPE_MAP.get(warn_var)}특보 발효",
                    station_id=None,
                )

    db.commit()
    return {"created": created, "newly_issued": newly_issued, "newly_cancelled": newly_cancelled}

WEATHER_DECAY_HOURS = 24  # 해제 후 24시간이면 영향 소멸

def get_weather_warning_weight(warning: WeatherWarning, now: datetime = None) -> float:
    now = now or datetime.now()
    if warning.is_active:
        return 1.0
    if not warning.cancelled_at:
        return 0.0
    elapsed_hours = (now - warning.cancelled_at).total_seconds() / 3600
    return max(0.0, 1 - elapsed_hours / WEATHER_DECAY_HOURS)