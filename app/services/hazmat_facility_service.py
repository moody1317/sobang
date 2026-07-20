import math
import requests
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.hazmat_facility import HazmatFacility

MERCATOR_R = 20037508.34

def mercator_to_wgs84(x: float, y: float) -> tuple[float, float]:
    """EPSG:3857(Web Mercator) 좌표 -> 위경도(WGS84). safemap.go.kr 응답의 x/y가 이 좌표계임을
    실제 샘플(대구 서구 평리동)을 역산해 확인함 — 위경도가 아님에 주의."""
    lon = x / MERCATOR_R * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(y / MERCATOR_R * math.pi)) - math.pi / 2)
    return lon, lat


def fetch_hazmat_facilities_raw(page_no: int = 1, num_of_rows: int = 100) -> ET.Element:
    params = {
        "serviceKey": settings.HAZMAT_FACILITY_API_KEY,
        "numOfRows": num_of_rows,
        "pageNo": page_no,
        "returnType": "xml",
    }
    response = requests.get(settings.HAZMAT_FACILITY_API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return ET.fromstring(response.text)


def _parse_item(item: ET.Element) -> dict:
    def text(tag):
        el = item.find(tag)
        return el.text if el is not None else None

    return {
        "objt_id": text("objt_id"),
        "entrps_nm": text("entrps_nm"),
        "induty_nm": text("induty_nm"),
        "adres": text("adres"),
        "rn_adres": text("rn_adres"),
        "ctprvn_cd": text("ctprvn_cd"),
        "sgg_cd": text("sgg_cd"),
        "emd_cd": text("emd_cd"),
        "x": text("x"),
        "y": text("y"),
        "bsum": text("bsum"),
    }


def sync_hazmat_facilities(db: Session) -> dict:
    first_page = fetch_hazmat_facilities_raw(page_no=1, num_of_rows=100)
    total_count = int(first_page.findtext(".//totalCount") or 0)

    existing_ids = {f.objt_id for f in db.query(HazmatFacility.objt_id).all()}

    created, updated = 0, 0
    page_no = 1
    while True:
        root = first_page if page_no == 1 else fetch_hazmat_facilities_raw(page_no=page_no, num_of_rows=100)
        items = root.findall(".//item")
        if not items:
            break

        for item in items:
            data = _parse_item(item)
            if not data["objt_id"]:
                continue
            objt_id = int(data["objt_id"])

            lat = lon = None
            if data["x"] and data["y"]:
                lon, lat = mercator_to_wgs84(float(data["x"]), float(data["y"]))

            if objt_id in existing_ids:
                facility = db.query(HazmatFacility).filter(HazmatFacility.objt_id == objt_id).first()
                updated += 1
            else:
                facility = HazmatFacility(objt_id=objt_id)
                db.add(facility)
                existing_ids.add(objt_id)
                created += 1

            facility.entrps_nm = data["entrps_nm"]
            facility.induty_nm = data["induty_nm"]
            facility.adres = data["adres"]
            facility.rn_adres = data["rn_adres"]
            facility.ctprvn_cd = int(data["ctprvn_cd"]) if data["ctprvn_cd"] else None
            facility.sgg_cd = int(data["sgg_cd"]) if data["sgg_cd"] else None
            facility.emd_cd = int(data["emd_cd"]) if data["emd_cd"] else None
            facility.latitude = lat
            facility.longitude = lon
            facility.bsum = float(data["bsum"]) if data["bsum"] else None

        db.commit()

        if page_no * 100 >= total_count:
            break
        page_no += 1

    return {"total": total_count, "created": created, "updated": updated}


def get_nearby_hazmat_facilities(db: Session, lat: float, lon: float, radius_km: float = 1.0) -> list[HazmatFacility]:
    from app.services.incident_service import haversine_distance

    candidates = (
        db.query(HazmatFacility)
        .filter(HazmatFacility.latitude.isnot(None), HazmatFacility.longitude.isnot(None))
        .all()
    )
    scored = sorted(
        ((f, haversine_distance(lat, lon, float(f.latitude), float(f.longitude))) for f in candidates),
        key=lambda pair: pair[1],
    )
    return [f for f, distance in scored if distance <= radius_km]
