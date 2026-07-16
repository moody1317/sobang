# app/api/v1/statistics.py
from datetime import datetime
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
from app.services.emergency_info_service import get_ems_hourly_buckets
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu, get_my_jurisdictions
from app.services.risk_score_service import get_my_dong_boundaries, resolve_risk_level

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


def _build_overview_for_year(db: Session, current_user: User, center_ids: list[int], sigungu_set: set, year: int) -> dict:
    year_start = f"{year}0101"
    year_end = f"{year}1231235959"  # rcpt_dt는 시분초까지 포함, dclr_ymd는 앞 8자리만 비교되므로 넉넉히 잡음

    fire_dates = [
        r[0] for r in db.query(FireIncident.rcpt_dt).filter(
            FireIncident.safety_center_id.in_(center_ids),
            FireIncident.rcpt_dt >= year_start,
            FireIncident.rcpt_dt <= year_end,
        ).all()
    ]

    ems_dates = [
        r[0] for r in db.query(EmsIncident.dclr_ymd).filter(
            EmsIncident.safety_center_id.in_(center_ids),
            EmsIncident.dclr_ymd >= year_start,
            EmsIncident.dclr_ymd <= f"{year}1231",
        ).all()
    ]

    mountain_count = (
        db.query(MountainAccident).filter(MountainAccident.gu_nm.in_(sigungu_set)).count()
        if sigungu_set else 0
    )

    total = len(fire_dates) + len(ems_dates)
    grand_total = total + mountain_count

    monthly = defaultdict(int)
    for d in fire_dates:
        if d:
            monthly[d[:6]] += 1
    for d in ems_dates:
        if d:
            monthly[d[:6]] += 1
    monthly_trend = [{"month": k, "count": v} for k, v in sorted(monthly.items())]

    type_breakdown = [
        {"type": "화재", "count": len(fire_dates), "ratio": round(len(fire_dates) / grand_total, 4) if grand_total else 0},
        {"type": "구급", "count": len(ems_dates), "ratio": round(len(ems_dates) / grand_total, 4) if grand_total else 0},
        {"type": "산악", "count": mountain_count, "ratio": round(mountain_count / grand_total, 4) if grand_total else 0},
    ]
    most_frequent_type = max(type_breakdown, key=lambda x: x["count"]) if grand_total else None

    hourly_buckets = {"심야": 0, "오전": 0, "오후": 0, "저녁": 0}
    fire_with_time = 0
    for d in fire_dates:
        if not d or len(d) < 10:
            continue
        hour = int(d[8:10])
        fire_with_time += 1
        if 0 <= hour < 6:
            hourly_buckets["심야"] += 1
        elif 6 <= hour < 12:
            hourly_buckets["오전"] += 1
        elif 12 <= hour < 18:
            hourly_buckets["오후"] += 1
        else:
            hourly_buckets["저녁"] += 1

    ems_hourly = {"buckets": {"심야": 0, "오전": 0, "오후": 0, "저녁": 0}, "total": 0}
    hourly_includes_ems = year == datetime.now().year
    if hourly_includes_ems:
        station = db.query(Station).filter(Station.id == current_user.station_id).first()
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
        "year": year,
        "total_dispatches": total,
        "most_frequent_type": most_frequent_type,
        "monthly_trend": monthly_trend,
        "type_breakdown": type_breakdown,
        "hourly_distribution": hourly_distribution,
        "hourly_includes_ems": hourly_includes_ems,
    }


def _get_dong_risk_summary(db: Session, current_user: User) -> dict:
    dongs = get_my_dong_boundaries(db, current_user)
    scores = [float(d.risk_score) for d in dongs if d.risk_score is not None]
    if not scores:
        return {"avg_risk_score": None, "high_risk_dong_count": None, "total_dong_count": len(dongs)}

    avg_risk_score = round(sum(scores) / len(scores), 1)
    high_risk_dong_count = sum(1 for s in scores if resolve_risk_level(s) == "danger")
    return {
        "avg_risk_score": avg_risk_score,
        "high_risk_dong_count": high_risk_dong_count,
        "total_dong_count": len(dongs),
    }


@router.get("/overview")
def get_statistics_overview(
    year: int | None = None,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    center_ids = get_my_safety_center_ids(db, current_user)
    sigungu_set = get_my_sigungu_set(db, current_user)

    if not center_ids:
        return {
            "year": year or datetime.now().year,
            "is_fallback_year": False,
            "total_dispatches": 0,
            "avg_risk_score": None,
            "high_risk_dong_count": None,
            "total_dong_count": 0,
            "most_frequent_type": None,
            "monthly_trend": [],
            "type_breakdown": [],
            "hourly_distribution": [],
        }

    requested_year = year or datetime.now().year
    result = _build_overview_for_year(db, current_user, center_ids, sigungu_set, requested_year)

    if not result["monthly_trend"] and year is None:
        fallback_year = requested_year - 1
        result = _build_overview_for_year(db, current_user, center_ids, sigungu_set, fallback_year)
        result["is_fallback_year"] = True
    else:
        result["is_fallback_year"] = False

    result.update(_get_dong_risk_summary(db, current_user))

    return result