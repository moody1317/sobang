# app/services/ems_incident_service.py
import json
import time
import subprocess
from app.core.config import settings
from sqlalchemy.orm import Session
from app.services.jurisdiction_service import normalize_name
from app.models.safety_center import SafetyCenter
from app.models.ems_incident import EmsIncident

def fetch_ems_incidents_raw(page: int = 1, size: int = 20, dspt_ymd_prefix: str = None, q: str = None, sort: str = None) -> dict:
    url = f"{settings.EMS_API_BASE_URL}?page={page}&size={size}"
    if dspt_ymd_prefix:
        url += f"&dsptYmd={dspt_ymd_prefix}"
    if q:
        url += f"&q={q}"
    if sort:
        url += f"&sort={sort}"

    result = subprocess.run(
        [
            "curl", "-s", "-S",
            "--retry", "5",
            "--retry-delay", "3",
            "--retry-all-errors",
            "-X", "POST", url,
            "-H", f"X-API-KEY: {settings.EMS_API_KEY}",
        ],
        capture_output=True, text=True, timeout=120, encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"curl 실행 실패 (code={result.returncode}): {result.stderr}")
    if not result.stdout.strip():
        raise RuntimeError("빈 응답")

    return json.loads(result.stdout)

def fetch_ems_incidents_preview(page: int = 1, size: int = 3) -> dict:
    return fetch_ems_incidents_raw(page=page, size=size)

def sync_ems_incidents(db: Session, start_ymd: str = "20250101", end_ymd: str = "20260630") -> dict:
    center_map = build_center_name_map(db)

    page = 1
    size = 100
    collected = 0
    failed_pages = []

    while True:
        try:
            result = fetch_ems_incidents_raw(page=page, size=size, sort="dclrYmd,desc")
        except (RuntimeError, Exception) as e:
            print(f"page {page} 실패, 건너뜀: {e}")
            failed_pages.append(page)
            page += 1
            continue

        items = result.get("items", [])
        if not items:
            break

        stop = False
        for item in items:
            dclr_ymd = item.get("dclrYmd")
            if not dclr_ymd:
                continue
            if dclr_ymd < start_ymd:
                stop = True
                continue
            if dclr_ymd > end_ymd:
                continue

            upsert_ems_incident(db, item, center_map)
            collected += 1

        db.commit()
        print(f"page {page} 처리 완료 — 누적 {collected}건")

        if stop or not result.get("hasNext"):
            break
        page += 1

    return {"collected": collected, "last_page": page, "failed_pages": failed_pages}

def build_center_name_map(db: Session) -> dict:
    """안전센터 이름(정규화) → id 매핑, 화재 서비스와 동일한 패턴"""
    centers = db.query(SafetyCenter).all()
    return {normalize_name(c.station_name): c.id for c in centers}

def upsert_ems_incident(db: Session, item: dict, center_map: dict):
    rlf_rptp_no = item.get("rlfRptpNo")
    if not rlf_rptp_no:
        return

    existing = db.query(EmsIncident).filter(EmsIncident.rlf_rptp_no == rlf_rptp_no).first()
    if existing:
        return 
    
    center_id = center_map.get(normalize_name(item.get("cntrNm") or ""))

    db.add(EmsIncident(
        rlf_rptp_no=rlf_rptp_no,
        reg_cmptn_se_nm=item.get("regCmptnSeNm"),
        dclr_ymd=item.get("dclrYmd"),
        dspt_ymd=item.get("dsptYmd"),
        grnds_arvl_ymd=item.get("grndsArvlYmd"),
        ctpv_nm=item.get("ctpvNm"),
        sggu_nm=item.get("sggNm"),
        frstn_nm=item.get("frstnNm"),
        cntr_nm=item.get("cntrNm"),
        ptn_ocrn_type_nm=item.get("ptnOcrnTypeNm"),
        ptn_sym_se_nm=item.get("ptnSymSeNm"),
        trfc_acdnt_se_nm=item.get("trfcAcdntSeNm"),
        safety_center_id=center_id,
    ))
