# app/api/v1/statistics.py
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User, UnitType
from app.models.safety_center import SafetyCenter
from app.models.station import Station
from app.models.jurisdiction import Jurisdiction
from app.models.fire_incident import FireIncident
from app.models.ems_incident import EmsIncident
from app.models.mountain_accident import MountainAccident
from app.models.rescue_accident import RescueAccident
from app.services.emergency_info_service import get_ems_hourly_buckets
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu, get_my_jurisdictions

router = APIRouter(prefix="/statistics", tags=["statistics"])


def get_my_safety_center_ids(db: Session, current_user: User) -> list[int]:
    jurisdictions = get_my_jurisdictions(db, current_user)
    return list({j.safety_center_id for j in jurisdictions if j.safety_center_id})


def get_my_sigungu_set(db: Session, current_user: User) -> set:
    """로그인 사용자 관할구역이 속한 시군구 이름 집합 (CSV 데이터의 gu_nm과 직접 매칭)"""
    if current_user.unit_type == UnitType.SAFETY_CENTER and current_user.safety_center_id:
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id == current_user.safety_center_id,
            Jurisdiction.is_active == True,
        ).all()
    else:
        center_ids = [
            c.id for c in db.query(SafetyCenter)
            .filter(SafetyCenter.parent_station_id == current_user.station_id)
            .all()
        ]
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id.in_(center_ids),
            Jurisdiction.is_active == True,
        ).all()

    sigungu_set = {get_jurisdiction_sigungu(db, j) for j in jurisdictions}
    sigungu_set.discard(None)
    return sigungu_set


@router.get("/overview")
def get_statistics_overview(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    center_ids = get_my_safety_center_ids(db, current_user)
    sigungu_set = get_my_sigungu_set(db, current_user)

    if not center_ids:
        return {
            "total_dispatches": 0,
            "avg_risk_score": None,
            "high_risk_jurisdiction_count": None,
            "most_frequent_type": None,
            "monthly_trend": [],
            "type_breakdown": [],
            "type_breakdown_notes": {},
            "hourly_distribution": [],
        }

    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

    # ── 화재 / 구급 이력 (최근 1년 실측) ──────────────────────────
    fires = db.query(FireIncident).filter(
        FireIncident.safety_center_id.in_(center_ids),
        FireIncident.rcpt_dt >= one_year_ago,
    ).all()

    ems = db.query(EmsIncident).filter(
        EmsIncident.safety_center_id.in_(center_ids),
        EmsIncident.dclr_ymd >= one_year_ago,
    ).all()

    # ── 산악 / 구조 (CSV 스냅샷, 2024년 연간 기준) ────────────────
    mountain_accidents = []
    rescue_accidents = []
    if sigungu_set:
        mountain_accidents = db.query(MountainAccident).filter(
            MountainAccident.gu_nm.in_(sigungu_set)
        ).all()
        rescue_accidents = db.query(RescueAccident).filter(
            RescueAccident.gu_nm.in_(sigungu_set)
        ).all()

    total = len(fires) + len(ems)
    grand_total = total + len(mountain_accidents) + len(rescue_accidents)

    # ── 월별 추이 (화재 + 구급만, 실측 기간 기준) ─────────────────
    monthly = defaultdict(int)
    for f in fires:
        if f.rcpt_dt:
            monthly[f.rcpt_dt[:6]] += 1
    for e in ems:
        if e.dclr_ymd:
            monthly[e.dclr_ymd[:6]] += 1
    monthly_trend = [{"month": k, "count": v} for k, v in sorted(monthly.items())]

    # ── 유형별 구성 ────────────────────────────────────────────
    type_breakdown = [
        {"type": "화재", "count": len(fires), "ratio": round(len(fires) / grand_total, 4) if grand_total else 0},
        {"type": "구급", "count": len(ems), "ratio": round(len(ems) / grand_total, 4) if grand_total else 0},
        {"type": "구조", "count": len(rescue_accidents), "ratio": round(len(rescue_accidents) / grand_total, 4) if grand_total else 0},
        {"type": "산악", "count": len(mountain_accidents), "ratio": round(len(mountain_accidents) / grand_total, 4) if grand_total else 0},
    ]
    type_breakdown_notes = {
        "화재": "최근 1년 실측",
        "구급": "최근 1년 실측",
        "구조": "2024년 연간 기준 (CSV 스냅샷, 최신 데이터 없음)",
        "산악": "2024년 연간 기준 (CSV 스냅샷, 최신 데이터 없음)",
    }
    most_frequent_type = max(type_breakdown, key=lambda x: x["count"]) if grand_total else None

    # ── 시간대별 분포 — 화재(실측) + 구급(구급정보서비스 실시간 보강) ──
    hourly_buckets = {"심야": 0, "오전": 0, "오후": 0, "저녁": 0}
    fire_with_time = 0
    for f in fires:
        if not f.rcpt_dt or len(f.rcpt_dt) < 10:
            continue
        hour = int(f.rcpt_dt[8:10])
        fire_with_time += 1
        if 0 <= hour < 6:
            hourly_buckets["심야"] += 1
        elif 6 <= hour < 12:
            hourly_buckets["오전"] += 1
        elif 12 <= hour < 18:
            hourly_buckets["오후"] += 1
        else:
            hourly_buckets["저녁"] += 1

    station = db.query(Station).filter(Station.id == current_user.station_id).first()
    ems_hourly = {"buckets": {"심야": 0, "오전": 0, "오후": 0, "저녁": 0}, "total": 0}
    if station:
        ems_hourly = get_ems_hourly_buckets(station.station_name, "충청북도")

    combined_buckets = dict(hourly_buckets)
    combined_total = fire_with_time
    for k in combined_buckets:
        combined_buckets[k] += ems_hourly["buckets"][k]
    combined_total += ems_hourly["total"]

    hourly_distribution = [
        {"slot": k, "ratio": round(v / combined_total, 4) if combined_total else 0}
        for k, v in combined_buckets.items()
    ]

    return {
        "total_dispatches": total,
        "avg_risk_score": None,               # 위험 스코어 산식 완성 후 반영 예정
        "high_risk_jurisdiction_count": None,  # 위험 스코어 산식 완성 후 반영 예정
        "most_frequent_type": most_frequent_type,
        "monthly_trend": monthly_trend,
        "type_breakdown": type_breakdown,
        "type_breakdown_notes": type_breakdown_notes,
        "hourly_distribution": hourly_distribution,
    }