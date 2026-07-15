# app/services/admin_dong_population_service.py
import requests
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.admin_dong_population import AdminDongPopulation

SIGUNGU_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "sigungu_codes.json"
with open(SIGUNGU_CODES_PATH, encoding="utf-8") as f:
    SIGUNGU_CODES = json.load(f)

def fetch_admin_dong_population_raw(
    admm_cd: str,
    srch_fr_ym: str,
    srch_to_ym: str,
    lv: str = "3",
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict:
    params = {
        "serviceKey": settings.ADMIN_DONG_POPULATION_API_KEY,
        "admmCd": admm_cd,
        "srchFrYm": srch_fr_ym,
        "srchToYm": srch_to_ym,
        "lv": lv,
        "regSeCd": "1",
        "type": "json",
        "numOfRows": num_of_rows,
        "pageNo": page_no,
    }
    response = requests.get(settings.ADMIN_DONG_POPULATION_API_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()

def parse_admin_dong_population(raw: dict) -> list[dict]:
    items = raw.get("Response", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]
    return items

def upsert_admin_dong_population(db: Session, item: dict):
    admin_code = item.get("admmCd")
    stats_ym = item.get("statsYm")
    if not admin_code or not stats_ym:
        return

    existing = db.query(AdminDongPopulation).filter(
        AdminDongPopulation.admin_code == admin_code,
        AdminDongPopulation.std_ym == stats_ym,
    ).first()

    values = dict(
        admin_code=admin_code,
        sido_nm=item.get("ctpvNm"),
        sigungu_nm=item.get("sggNm"),
        dong_nm=item.get("dongNm"),
        std_ym=stats_ym,
        total_ppltn=int(item.get("totNmprCnt") or 0),
        male_ppltn=int(item.get("maleNmprCnt") or 0),
        female_ppltn=int(item.get("femlNmprCnt") or 0),
        elderly_ppltn=sum(
            int(item.get(f"{g}{age}AgeNmprCnt") or 0)
            for g in ("male", "feml")
            for age in (60, 70, 80, 90, 100)
        ),
    )

    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
    else:
        db.add(AdminDongPopulation(**values))

def sync_admin_dong_population(db: Session, srch_fr_ym: str, srch_to_ym: str) -> dict:
    """법정동 인구 sync와 동일한 패턴 — 272개 시군구 순회, lv=3(읍면동 단위)"""
    total_created, total_updated = 0, 0
    failed = []

    for entry in SIGUNGU_CODES:
        code = entry["code"]
        try:
            raw = fetch_admin_dong_population_raw(code, srch_fr_ym, srch_to_ym, lv="3", num_of_rows=100)
            items = parse_admin_dong_population(raw)

            for item in items:
                upsert_admin_dong_population(db, item)

            db.commit()
            total_created += len(items)

        except Exception as e:
            failed.append({"code": code, "sigungu": entry["sigungu"], "error": str(e)})

    return {"processed": total_created, "failed": failed}