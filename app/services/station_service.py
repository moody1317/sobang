import xml.etree.ElementTree as ET

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.station import Station

FIELD_MAP = {
    "objt_id": "objt_id",
    "fclty_nm": "fclty_nm",
    "fclty_ty": "fclty_ty",
    "fclty_cd": "fclty_cd",
    "rn_adres": "rn_adres",
    "telno": "telno",
}


def fetch_station_raw(page_no: int = 1, num_of_rows: int = 100) -> str:
    """외부 API 전체 응답(XML 원문)을 가져온다."""
    params = {
        "serviceKey": settings.STATION_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "returnType": "XML",
    }
    response = requests.get(settings.STATION_API_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.text


def fetch_station_data(page_no: int = 1, num_of_rows: int = 10):
    """디버깅/테스트용 미리보기 (기존 동작 유지)"""
    text = fetch_station_raw(page_no, num_of_rows)
    return {
        "status_code": 200,
        "body_preview": text[:5000],
    }


def fetch_total_count(num_of_rows: int = 1) -> int:
    """전체 데이터 개수 확인용 (1건만 요청해서 totalCount만 본다)"""
    params = {
        "serviceKey": settings.STATION_API_KEY,
        "pageNo": 1,
        "numOfRows": num_of_rows,
        "returnType": "XML",
    }
    response = requests.get(settings.STATION_API_BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    total = root.findtext(".//totalCount")
    return int(total) if total else 0


def parse_station_xml(xml_text: str) -> list[dict]:
    """XML 응답을 station 딕셔너리 리스트로 변환"""
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")

    parsed = []
    for item in items:
        data = {}
        for child in item:
            field = FIELD_MAP.get(child.tag)
            if field:
                data[field] = (child.text or "").strip()

        if data.get("objt_id"):
            parsed.append(data)

    return parsed


def upsert_stations(db: Session, station_list: list[dict]) -> dict:
    """station_code(objt_id) 기준으로 있으면 업데이트, 없으면 생성"""
    created, updated = 0, 0

    for s in station_list:
        fclty_ty = s.get("fclty_ty", "")
        fclty_nm = s.get("fclty_nm", "")
        unit_type = classify_unit_type(fclty_ty, fclty_nm)

        existing = (
            db.query(Station)
            .filter(Station.station_code == s["objt_id"])
            .first()
        )

        if existing:
            existing.station_name = fclty_nm or existing.station_name
            existing.fclty_ty = fclty_ty or existing.fclty_ty
            existing.unit_type = unit_type
            existing.address = s.get("rn_adres", existing.address)
            existing.phone_number = s.get("telno", existing.phone_number)
            updated += 1
        else:
            db.add(Station(
                station_code=s["objt_id"],
                station_name=fclty_nm or "이름없음",
                fclty_ty=fclty_ty,
                unit_type=unit_type,
                address=s.get("rn_adres"),
                phone_number=s.get("telno"),
            ))
            created += 1

    db.commit()
    return {"created": created, "updated": updated}


def sync_all_stations(db: Session, num_of_rows: int = 500) -> dict:
    """전체 페이지를 자동으로 돌면서 동기화"""
    total_count = fetch_total_count()
    if total_count == 0:
        return {"created": 0, "updated": 0, "total_pages": 0}

    total_pages = (total_count + num_of_rows - 1) // num_of_rows

    total_created, total_updated = 0, 0

    for page in range(1, total_pages + 1):
        raw_xml = fetch_station_raw(page_no=page, num_of_rows=num_of_rows)
        parsed = parse_station_xml(raw_xml)
        result = upsert_stations(db, parsed)
        total_created += result["created"]
        total_updated += result["updated"]

    return {
        "created": total_created,
        "updated": total_updated,
        "total_pages": total_pages,
    }

def classify_unit_type(fclty_ty: str, fclty_nm: str) -> str:
    """fclty_ty + fclty_nm 기반으로 UnitType 값을 결정"""
    if fclty_ty == "소방서":
        return "본서"
    
    if fclty_ty == "119안전센터":
        return "안전센터"
    
    if "지역대" in fclty_nm:
        return "지역대"
    if "항공대" in fclty_nm:
        return "항공대"
    if "구급대" in fclty_nm:
        return "구급대"
    if "특수대응단" in fclty_nm:
        return "특수대응단"
    
    return "기타"