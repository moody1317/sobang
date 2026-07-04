# app/services/fire_target_service.py
import json
import subprocess
from urllib.parse import quote
from app.core.config import settings
from sqlalchemy.orm import Session
from app.services.jurisdiction_service import normalize_name
from app.models.safety_center import SafetyCenter
from app.models.fire_target import FireTarget

FIRE_TARGETS_URL = "https://www.bigdata-119.kr/fsdpApi/rest/v1/fire-targets"


def fetch_fire_targets_raw(page: int = 1, size: int = 20, q: str = None, sort: str = None) -> dict:
    url = f"{FIRE_TARGETS_URL}?page={page}&size={size}"
    if q:
        url += f"&q={quote(q)}"
    if sort:
        url += f"&sort={quote(sort)}"

    result = subprocess.run(
        ["curl", "-s", "-X", "POST", url, "-H", f"X-API-KEY: {settings.EMS_API_KEY}"],
        capture_output=True, text=True, timeout=30, encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl 실행 실패: {result.stderr}")
    if not result.stdout.strip():
        raise RuntimeError(f"빈 응답. stderr: {result.stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("JSON 파싱 실패, 원문:")
        print(result.stdout[:1000])
        raise

def build_center_name_map(db: Session) -> dict:
    centers = db.query(SafetyCenter).all()
    return {normalize_name(c.station_name): c.id for c in centers}

def upsert_fire_target(db: Session, item: dict, center_map: dict):
    bdst_sn = item.get("bdstSn")
    if not bdst_sn:
        return False

    existing = db.query(FireTarget).filter(FireTarget.bdst_sn == bdst_sn).first()

    center_id = center_map.get(normalize_name(item.get("cntrNm") or ""))

    values = dict(
        bdst_sn=bdst_sn,
        trgtobj_nm=item.get("trgtobjNm"),
        bldg_nm=item.get("bldgNm"),
        addr=item.get("addr"),
        ctpv_nm=item.get("ctpvNm"),
        sggu_nm=item.get("sggNm"),
        emd_nm=item.get("emdNm"),
        frstn_nm=item.get("frstnNm"),
        cntr_nm=item.get("cntrNm"),
        use_yn=(item.get("useYn") or "").strip() or None,
        lgz_fire_wktrgt_yn=(item.get("lgzFireWktrgtYn") or "").strip() or None,
        isf_chck_trgt_yn=(item.get("isfChckTrgtYn") or "").strip() or None,
        isf_chck_trgt_type_nm=item.get("isfChckTrgtTypeNm"),
        cltpty_yn=(item.get("cltptyYn") or "").strip() or None,
        pbnst_yn=(item.get("pbnstYn") or "").strip() or None,
        arson_mng_trgt_yn=(item.get("arsonMngTrgtYn") or "").strip() or None,
        fire_insrnc_co_nm=item.get("fireInsrncCoNm"),
        fire_insrnc_join_ymd=item.get("fireInsrncJoinYmd"),
        use_aprv_ymd=item.get("useAprvYmd"),
        safety_center_id=center_id,
    )

    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
        return False
    else:
        db.add(FireTarget(**values))
        return True

def sync_fire_targets(db: Session) -> dict:
    center_map = build_center_name_map(db)

    page = 1
    size = 100
    created, updated = 0, 0

    while True:
        result = fetch_fire_targets_raw(page=page, size=size)
        items = result.get("items", [])
        if not items:
            break

        for item in items:
            is_new = upsert_fire_target(db, item, center_map)
            if is_new:
                created += 1
            else:
                updated += 1

        db.commit()   # 화재 때 배운 교훈 — 페이지마다 커밋해서 중간에 끊겨도 안전하게
        print(f"page {page} 완료 — 누적 생성 {created}, 갱신 {updated}")
        
        if not result.get("hasNext"):
            break
        page += 1

    return {"created": created, "updated": updated, "last_page": page}