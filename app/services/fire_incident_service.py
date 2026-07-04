import json
import subprocess
from urllib.parse import quote
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.jurisdiction_service import normalize_name
from app.models.safety_center import SafetyCenter
from app.models.fire_incident import FireIncident

FIRE_INCIDENTS_URL = "https://www.bigdata-119.kr/fsdpApi/rest/v1/fire-incidents"

def fetch_fire_incidents_raw(page: int = 1, size: int = 20, q: str = None, sort: str = None, rcpt_dt_prefix: str = None) -> dict:
    url = f"{FIRE_INCIDENTS_URL}?page={page}&size={size}"
    if q:
        url += f"&q={quote(q)}"          # URL 인코딩 추가
    if sort:
        url += f"&sort={quote(sort)}"
    if rcpt_dt_prefix:
        url += f"&rcptDt={rcpt_dt_prefix}"

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", f"X-API-KEY: {settings.EMS_API_KEY}"],
        capture_output=True, text=True, timeout=30, encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"curl 실행 실패(returncode={result.returncode}): {result.stderr}")

    if not result.stdout.strip():
        raise RuntimeError(f"빈 응답 옴. stderr: {result.stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("JSON 파싱 실패, 원문 응답:")
        print(result.stdout[:1000])
        raise

def fetch_fire_incidents_preview(page: int = 1, size: int = 3) -> dict:
    return fetch_fire_incidents_raw(page=page, size=size)

def match_center_by_name(db: Session, cntr_nm: str):
    if not cntr_nm:
        return None
    normalized = normalize_name(cntr_nm)
    centers = db.query(SafetyCenter).all()
    for c in centers:
        if normalized == normalize_name(c.station_name):
            return c.id
    return None

def build_center_name_map(db: Session) -> dict:
    centers = db.query(SafetyCenter).all()
    return {normalize_name(c.station_name): c.id for c in centers}

def get_season_from_dt(dt_str: str) -> str | None:
    """YYYYMMDDHHMMSS 형식 문자열에서 월을 뽑아 계절 반환"""
    if not dt_str or len(dt_str) < 6:
        return None
    month = int(dt_str[4:6])
    if month in (12, 1, 2):
        return "겨울"
    elif month in (3, 4, 5):
        return "봄"
    elif month in (6, 7, 8):
        return "여름"
    else:
        return "가을"
    
def upsert_fire_incident(db: Session, item: dict, center_map: dict):
    wrinv_no = item.get("wrinvNo")
    if not wrinv_no:
        return

    existing = db.query(FireIncident).filter(FireIncident.wrinv_no == wrinv_no).first()

    weather_fields = dict(
        seasn_nm=get_season_from_dt(item.get("rcptDt")),
        dow_nm=item.get("dowNm"),
        hr_unit_artmp=item.get("hrUnitArtmp"),
        hr_unit_hum=item.get("hrUnitHum"),
        hr_unit_wspd_info=item.get("hrUnitWspdInfo"),
    )

    if existing:
        for k, v in weather_fields.items():
            setattr(existing, k, v)
        return

    center_id = center_map.get(normalize_name(item.get("cntrNm") or ""))

    db.add(FireIncident(
        wrinv_no=wrinv_no,
        rcpt_dt=(item.get("rcptDt") or "").strip() or None,
        dspt_dt=(item.get("dsptDt") or "").strip() or None,
        grnds_arvl_dt=(item.get("grndsArvlDt") or "").strip() or None,
        prfect_potfr_dt=(item.get("prfectPotfrDt") or "").strip() or None,
        ctpv_nm=item.get("ctpvNm"),
        sggu_nm=item.get("sggNm"),
        frstn_nm=item.get("frstnNm"),
        cntr_nm=item.get("cntrNm"),
        fire_type_nm=item.get("fireTypeNm"),
        fclt_plc_lclsf_nm=item.get("fcltPlcLclsfNm"),
        igtn_dmnt_lclsf_nm=item.get("igtnDmntLclsfNm"),
        dth_cnt=item.get("dthCnt"),
        injpsn_cnt=item.get("injpsnCnt"),
        prpt_dam_amt=item.get("prptDamAmt"),
        fire_supesn_hr=item.get("fireSupesnHr"),
        safety_center_id=center_id,
        **weather_fields,
    ))

def sync_fire_incidents(db: Session, start_ymd: str = "20250101", end_ymd: str = "20260630") -> dict:
    center_map = build_center_name_map(db)
    start_dt = start_ymd + "000000"
    page = 1
    size = 100
    collected = 0
    skipped_out_of_range = 0

    while True:
        result = fetch_fire_incidents_raw(page=page, size=size, sort="rcptDt,desc")
        items = result.get("items", [])
        if not items:
            break

        stop = False
        for item in items:
            rcpt_dt = (item.get("rcptDt") or "").strip()
            if not rcpt_dt:
                continue
            if rcpt_dt < start_dt:
                stop = True
                continue
            if rcpt_dt[:8] > end_ymd:
                skipped_out_of_range += 1
                continue

            upsert_fire_incident(db, item, center_map)
            collected += 1

        db.commit()
        print(f"page {page} 처리 완료 — 누적 수집 {collected}건")

        if stop or not result.get("hasNext"):
            break
        page += 1

    return {"collected": collected, "skipped_out_of_range": skipped_out_of_range, "last_page": page}