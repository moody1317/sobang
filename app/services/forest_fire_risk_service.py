import requests
import json
from app.core.config import settings
from sqlalchemy.orm import Session
from pathlib import Path
from app.models.forest_fire_risk import ForestFireRisk
from app.models.jurisdiction import Jurisdiction
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu

SIGUNGU_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "sigungu_codes.json"
with open(SIGUNGU_CODES_PATH, encoding="utf-8") as f:
    _SIGUNGU_NAME_TO_CODE5 = {entry["sigungu"]: entry["code"][:5] for entry in json.load(f)}

def get_forest_fire_sigu_code(sigungu_full_name: str) -> str | None:
    """'청주시 상당구' 같은 일반구 이름이면 상위 'OO시' 코드로 폴백"""
    code = _SIGUNGU_NAME_TO_CODE5.get(sigungu_full_name)
    if code:
        return code
    if " " in sigungu_full_name:
        city_name = sigungu_full_name.split(" ")[0]
        return _SIGUNGU_NAME_TO_CODE5.get(city_name)
    return None

def allocate_forest_fire_risk_to_jurisdictions(db: Session) -> dict:
    jurisdictions = db.query(Jurisdiction).filter(Jurisdiction.is_active == True).all()
    risk_by_code = {r.sigu_code: r for r in db.query(ForestFireRisk).all()}

    allocated = 0
    not_found = []

    for j in jurisdictions:
        sigungu = get_jurisdiction_sigungu(db, j)
        if not sigungu:
            not_found.append(j.ward_name)
            continue

        code = _SIGUNGU_NAME_TO_CODE5.get(sigungu)
        risk = risk_by_code.get(code) if code else None

        if not risk and " " in sigungu:
            city_name = sigungu.split(" ")[0]
            city_code = _SIGUNGU_NAME_TO_CODE5.get(city_name)
            risk = risk_by_code.get(city_code) if city_code else None

        if risk:
            j.forest_fire_risk_index = risk.mean_index
            allocated += 1
        else:
            not_found.append(j.ward_name)

    db.commit()
    return {"allocated": allocated, "not_found": not_found}

def fetch_forest_fire_risk_raw(page_no: int = 1, num_of_rows: int = 300) -> dict:
    params = {
        "ServiceKey": settings.FOREST_FIRE_API_KEY,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "_type": "json",
    }
    response = requests.get(settings.FOREST_FIRE_API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def fetch_forest_fire_risk_preview(num_of_rows: int = 5) -> dict:
    return fetch_forest_fire_risk_raw(num_of_rows=num_of_rows)

def parse_forest_fire_risk(raw: dict) -> list[dict]:
    items = raw.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]
    return items

def upsert_forest_fire_risk(db: Session, item: dict):
    sigu_code = str(item.get("sigucode"))
    if not sigu_code:
        return

    def to_num(v):
        if v is None:
            return None
        return str(v).replace(",", "")

    existing = db.query(ForestFireRisk).filter(ForestFireRisk.sigu_code == sigu_code).first()

    values = dict(
        sigu_code=sigu_code,
        sido_nm=item.get("doname"),
        sigungu_nm=item.get("sigun"),
        upplocalcd=str(item.get("upplocalcd")),
        mean_index=to_num(item.get("meanavg")),
        max_index=to_num(item.get("maxi")),
        min_index=to_num(item.get("mini")),
        std_index=to_num(item.get("std")),
        area_low=to_num(item.get("d1")),
        area_mid=to_num(item.get("d2")),
        area_high=to_num(item.get("d3")),
        area_very_high=to_num(item.get("d4")),
        analdate=item.get("analdate"),
    )

    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
    else:
        db.add(ForestFireRisk(**values))

def sync_forest_fire_risk(db: Session) -> dict:
    raw = fetch_forest_fire_risk_raw(num_of_rows=300)
    items = parse_forest_fire_risk(raw)

    for item in items:
        upsert_forest_fire_risk(db, item)

    db.commit()
    return {"synced": len(items)}