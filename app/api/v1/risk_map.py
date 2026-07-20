# app/api/v1/risk_map.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.services.risk_score_service import get_my_dong_boundaries, get_dong_risk_history

router = APIRouter(prefix="/risk-map", tags=["risk-map"])


@router.get("/dongs")
def get_risk_map_dongs(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    my_boundaries = get_my_dong_boundaries(db, current_user)

    return [
        {
            "admin_code": d.admin_code,
            "dong_nm": d.dong_nm,
            "sigungu_nm": d.sigungu_nm,
            "sido_nm": d.sido_nm,
            "geometry": d.geometry,
            "risk_score": float(d.risk_score) if d.risk_score is not None else None,
            "risk_score_breakdown": d.risk_score_breakdown,
            "risk_score_updated_at": d.risk_score_updated_at,
        }
        for d in my_boundaries
    ]

@router.get("/dongs/{admin_code}/history")
def get_dong_history(
    admin_code: str,
    weeks: int = Query(8, ge=1, le=52),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    snapshots = get_dong_risk_history(db, admin_code, weeks)
    return [
        {"snapshot_date": s.snapshot_date.isoformat(), "risk_score": float(s.risk_score)}
        for s in snapshots
    ]