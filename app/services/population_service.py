import xml.etree.ElementTree as ET
import requests
import json
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.population_stat import PopulationStat

FIELD_MAP = {
    "statsYm": "statsYm",
    "stdgCd": "stdgCd",
    "ctpvNm": "ctpvNm",
    "sggNm": "sggNm",
    "stdgNm": "stdgNm",
    "liNm": "liNm",
    "admmCd": "admmCd",
    "dongNm": "dongNm",
    "tong": "tong",
    "ban": "ban",
    "totNmprCnt": "totNmprCnt",
    "maleNmprCnt": "maleNmprCnt",
    "femlNmprCnt": "femlNmprCnt",
}
ELDERLY_MALE_FIELDS = ["male60AgeNmprCnt", "male70AgeNmprCnt", "male80AgeNmprCnt", "male90AgeNmprCnt", "male100AgeNmprCnt"]
ELDERLY_FEMALE_FIELDS = ["feml60AgeNmprCnt", "feml70AgeNmprCnt", "feml80AgeNmprCnt", "feml90AgeNmprCnt", "feml100AgeNmprCnt"]

SIGUNGU_CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "sigungu_codes.json"

def load_sigungu_codes() -> list[dict]:
    with open(SIGUNGU_CODES_PATH, encoding="utf-8") as f:
        return json.load(f)


def upsert_population_stats(db: Session, rows: list[dict]) -> dict:
    created, updated = 0, 0
    for r in rows:
        admm_cd = r.get("admmCd")
        stats_ym = r.get("statsYm")
        if not admm_cd or not stats_ym:
            continue

        existing = (
            db.query(PopulationStat)
            .filter(
                PopulationStat.admin_code == admm_cd,
                PopulationStat.std_ym == stats_ym,
            )
            .first()
        )

        values = dict(
            admin_code=admm_cd,
            sido_nm=r.get("ctpvNm"),
            sigungu_nm=r.get("sggNm"),
            hjd_nm=r.get("dongNm"),
            std_ym=stats_ym,
            total_ppltn=int(r.get("totNmprCnt") or 0),
            male_ppltn=int(r.get("maleNmprCnt") or 0),
            female_ppltn=int(r.get("femlNmprCnt") or 0),
            elderly_ppltn=int(r.get("elderly_ppltn") or 0),
        )

        if existing:
            for k, v in values.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(PopulationStat(**values))
            created += 1

    db.commit()
    return {"created": created, "updated": updated}


def sync_all_population(db: Session, srch_fr_ym: str, srch_to_ym: str) -> dict:
    """272개 시군구 코드를 순회하며 읍면동 단위(lv=3) 인구 데이터를 동기화"""
    sigungu_codes = load_sigungu_codes()
    total_created, total_updated = 0, 0
    failed = []

    for entry in sigungu_codes:
        code = entry["code"]
        try:
            total_count = fetch_total_count(code, srch_fr_ym, srch_to_ym, lv="3")
            if total_count == 0:
                continue

            num_of_rows = 100
            total_pages = (total_count + num_of_rows - 1) // num_of_rows

            for page in range(1, total_pages + 1):
                raw_xml = fetch_population_raw(
                    code, srch_fr_ym, srch_to_ym, lv="3",
                    page_no=page, num_of_rows=num_of_rows,
                )
                parsed = parse_population_xml(raw_xml)
                result = upsert_population_stats(db, parsed)
                total_created += result["created"]
                total_updated += result["updated"]

        except Exception as e:
            failed.append({"code": code, "sigungu": entry["sigungu"], "error": str(e)})

    return {
        "created": total_created,
        "updated": total_updated,
        "failed": failed,
    }

def fetch_population_raw(
    stdg_cd: str,
    srch_fr_ym: str,
    srch_to_ym: str,
    lv: str = "4",
    page_no: int = 1,
    num_of_rows: int = 100,
) -> str:
    params = {
        "serviceKey": settings.POPULATION_API_KEY,
        "stdgCd": stdg_cd,
        "srchFrYm": srch_fr_ym,
        "srchToYm": srch_to_ym,
        "lv": lv,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "type": "xml",
    }
    response = requests.get(settings.POPULATION_API_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.text

def fetch_population_preview(
    stdg_cd: str,
    srch_fr_ym: str,
    srch_to_ym: str,
    lv: str = "3",
    num_of_rows: int = 5,
):
    text = fetch_population_raw(stdg_cd, srch_fr_ym, srch_to_ym, lv=lv, num_of_rows=num_of_rows)
    return {"body_preview": text[:5000]}

def fetch_total_count(stdg_cd: str, srch_fr_ym: str, srch_to_ym: str, lv: str = "4") -> int:
    params = {
        "serviceKey": settings.POPULATION_API_KEY,
        "stdgCd": stdg_cd,
        "srchFrYm": srch_fr_ym,
        "srchToYm": srch_to_ym,
        "lv": lv,
        "pageNo": 1,
        "numOfRows": 1,
        "type": "xml",
    }
    response = requests.get(settings.POPULATION_API_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    total = root.findtext(".//totalCount")
    return int(total) if total else 0


def parse_population_xml(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")

    parsed = []
    for item in items:
        data = {child.tag.strip(): (child.text or "").strip() for child in item}

        elderly_male = sum(int(data.get(f, 0) or 0) for f in ELDERLY_MALE_FIELDS)
        elderly_female = sum(int(data.get(f, 0) or 0) for f in ELDERLY_FEMALE_FIELDS)
        data["elderly_ppltn"] = elderly_male + elderly_female

        parsed.append(data)

    return parsed