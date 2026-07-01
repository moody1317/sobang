import requests
from app.core.config import settings
from app.models.jurisdiction import Jurisdiction
from app.models.station import Station
from app.models.safety_center import SafetyCenter
from sqlalchemy.orm import Session
import re

VWORLD_WFS_URL = "https://api.vworld.kr/req/wfs"

# 시도별 대략적인 경계 (WGS84 경도,위도 기준)
PROVINCE_BBOXES = {
    "서울_동": "126.95,37.45,127.3,37.7",
    "서울_서": "126.6,37.45,126.97,37.7",

    "부산_동": "129.0,34.9,129.4,35.4",
    "부산_서": "128.6,34.9,129.05,35.4",

    "대구": "128.3,35.6,128.9,36.1",
    "인천": "126.1,37.1,126.9,37.8",
    "광주": "126.6,34.9,127.1,35.4",
    "대전": "127.1,36.1,127.7,36.6",
    "울산": "129.0,35.3,129.6,35.8",
    "세종": "127.0,36.3,127.5,36.8",

    "경기_북부": "126.3,37.4,127.9,38.4",
    "경기_남부": "126.3,36.8,127.9,37.45",

    "강원_영동": "127.9,37.0,129.6,38.8",
    "강원_영서": "126.9,37.0,128.0,38.6",

    "충북": "127.1,35.9,128.6,37.4",
    "충남": "125.9,35.8,127.5,37.2",
    "전북": "126.3,35.0,127.8,36.3",

    "전남_동": "126.6,33.8,127.9,35.7",
    "전남_서": "125.5,33.8,126.7,35.4",

    "경북_북부": "127.9,36.2,129.8,37.2",
    "경북_남부": "127.9,35.5,129.8,36.25",

    "경남_동": "128.4,34.6,129.4,36.0",
    "경남_서": "127.3,34.6,128.45,35.9",

    "제주": "125.9,32.9,127.1,33.7",
}

SUFFIX_TOKENS = [
    "지역119센터", "소방정안전센터", "지역센터",
    "119", "안전센터", "센터",
]

def fetch_jurisdiction_geojson(bbox: str) -> dict:
    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typename": "lt_c_usfsffb",
        "key": settings.VWORLD_API_KEY,
        "domain": "localhost",
        "srsName": "EPSG:4326",
        "output": "application/json",
        "bbox": bbox,
    }

    response = requests.get(VWORLD_WFS_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_all_jurisdictions() -> list[dict]:
    from collections import defaultdict

    grouped = defaultdict(lambda: {"properties": None, "geometries": []})

    for region_name, bbox in PROVINCE_BBOXES.items():
        data = fetch_jurisdiction_geojson(bbox=bbox)
        features = data.get("features", [])
        print(f"{region_name}: {len(features)}건")

        for f in features:
            props = f.get("properties", {})
            ward_id = props.get("ward_id")
            if not ward_id:
                continue

            grouped[ward_id]["properties"] = props          # 속성은 동일하니 덮어써도 무방
            grouped[ward_id]["geometries"].append(f.get("geometry"))

    # 최종 결과: ward_id당 하나의 항목, geometry는 조각 리스트(MultiPolygon으로 합칠 재료)
    result = []
    for ward_id, data in grouped.items():
        result.append({
            "ward_id": ward_id,
            "properties": data["properties"],
            "geometries": data["geometries"],   # 조각이 여러 개면 합쳐서 MultiPolygon으로 저장
        })

    return result

def parse_jurisdiction_features(features: list[dict]) -> list[dict]:
    parsed = []
    for f in features:
        properties = f.get("properties", {})
        geometry = f.get("geometry", {})
        parsed.append({
            "properties": properties,
            "geometry": geometry,
        })
    return parsed

def normalize_name(name: str) -> str:
    result = name
    for token in SUFFIX_TOKENS:
        result = result.replace(token, "")
    return re.sub(r"\s", "", result)

def rematch_unmatched_jurisdictions(db: Session) -> dict:
    unmatched = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.station_id.is_(None), Jurisdiction.safety_center_id.is_(None))
        .all()
    )

    all_centers = db.query(SafetyCenter).all()
    all_stations = db.query(Station).all()

    def match_ward(ward_name: str):
        normalized_ward = normalize_name(ward_name)

        for center in all_centers:
            normalized_center = normalize_name(center.station_name)
            if normalized_ward in normalized_center or normalized_center in normalized_ward:
                return None, center.id

        for station in all_stations:
            normalized_station = normalize_name(station.station_name)
            if normalized_ward in normalized_station or normalized_station in normalized_ward:
                return station.id, None

        return None, None

    matched = 0
    still_unmatched = []

    for j in unmatched:
        station_id, safety_center_id = match_ward(j.ward_name)
        if station_id or safety_center_id:
            j.station_id = station_id
            j.safety_center_id = safety_center_id
            matched += 1
        else:
            still_unmatched.append(j.ward_name)

    db.commit()
    return {"matched": matched, "still_unmatched": still_unmatched}

def match_ward_to_db(db: Session, ward_name: str):
    normalized_ward = normalize_name(ward_name)

    centers = db.query(SafetyCenter).all()
    for center in centers:
        normalized_center = normalize_name(center.station_name)   # center_name → station_name
        if normalized_ward in normalized_center or normalized_center in normalized_ward:
            return None, center.id

    stations = db.query(Station).all()
    for station in stations:
        normalized_station = normalize_name(station.station_name)
        if normalized_ward in normalized_station or normalized_station in normalized_ward:
            return station.id, None

    return None, None

def save_jurisdictions(db: Session, jurisdiction_data: list[dict]) -> dict:
    matched, unmatched = 0, 0
    unmatched_names = []

    all_centers = db.query(SafetyCenter).all()
    all_stations = db.query(Station).all()

    def match_ward(ward_name: str):
        normalized_ward = normalize_name(ward_name)

        for center in all_centers:
            normalized_center = normalize_name(center.station_name)   # center_name → station_name
            if normalized_ward in normalized_center or normalized_center in normalized_ward:
                return None, center.id

        for station in all_stations:
            normalized_station = normalize_name(station.station_name)
            if normalized_ward in normalized_station or normalized_station in normalized_ward:
                return station.id, None

        return None, None

    for item in jurisdiction_data:
        ward_id = item["ward_id"]
        properties = item["properties"]
        ward_name = properties.get("ward_nm", "")
        geometry = to_multipolygon(item["geometries"])

        station_id, safety_center_id = match_ward(ward_name)
        
        existing = db.query(Jurisdiction).filter(Jurisdiction.ward_id == ward_id).first()
        if existing:
            existing.ward_name = ward_name
            existing.station_id = station_id
            existing.safety_center_id = safety_center_id
            existing.geometry = geometry
        else:
            db.add(Jurisdiction(
                ward_id=ward_id,
                ward_name=ward_name,
                station_id=station_id,
                safety_center_id=safety_center_id,
                geometry=geometry,
            ))

        if station_id or safety_center_id:
            matched += 1
        else:
            unmatched += 1
            unmatched_names.append(ward_name)

    db.commit()
    return {"matched": matched, "unmatched": unmatched, "unmatched_names": unmatched_names}


def to_multipolygon(geometries: list[dict]) -> dict:
    coordinates = []
    for geom in geometries:
        if geom["type"] == "Polygon":
            coordinates.append(geom["coordinates"])
        elif geom["type"] == "MultiPolygon":
            coordinates.extend(geom["coordinates"])

    return {
        "type": "MultiPolygon",
        "coordinates": coordinates,
    }