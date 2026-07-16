# app/api/v1/risk_map.py
from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.jurisdiction_dong import JurisdictionDong
from app.models.admin_dong_boundary import AdminDongBoundary
from app.services.jurisdiction_population_service import get_my_jurisdictions
from app.services.risk_score_service import dong_key

router = APIRouter(prefix="/risk-map", tags=["risk-map"])


@router.get("/dongs")
def get_risk_map_dongs(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    jurisdictions = get_my_jurisdictions(db, current_user)
    jurisdiction_ids = [j.id for j in jurisdictions]
    if not jurisdiction_ids:
        return []

    jurisdiction_dongs = (
        db.query(JurisdictionDong).filter(JurisdictionDong.jurisdiction_id.in_(jurisdiction_ids)).all()
    )
    if not jurisdiction_dongs:
        return []

    # jurisdiction_dongs는 소규모 테이블이라 여기서 SQL 조건을 만들어, admin_dong_boundaries에서
    # 필요한 동의 geometry만 가져온다 (전국 3천여 건을 전부 읽어와 Python에서 거르지 않도록).
    match_conditions = [
        and_(AdminDongBoundary.sigungu_nm == jd.sigungu_nm, AdminDongBoundary.dong_nm == jd.dong_nm)
        for jd in jurisdiction_dongs
    ]
    candidates = (
        db.query(AdminDongBoundary)
        .filter(AdminDongBoundary.geometry.isnot(None), or_(*match_conditions))
        .all()
    )

    # 마침표·"제"+숫자·유니코드 정규화 차이로 위 SQL 조건에 안 걸리는 극소수 케이스를 대비한 안전망.
    # candidates가 이미 관할동 규모로 좁혀진 뒤라 비용이 크지 않다.
    my_dong_keys = {dong_key(jd.sigungu_nm, jd.dong_nm) for jd in jurisdiction_dongs}
    my_boundaries = [b for b in candidates if dong_key(b.sigungu_nm, b.dong_nm) in my_dong_keys]

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