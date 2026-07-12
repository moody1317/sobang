# app/api/v1/weather.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User, UnitType
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter
from app.models.weather_warning import WeatherWarning
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu, extract_city_name

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/warnings")
def get_my_weather_warnings(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.unit_type == UnitType.SAFETY_CENTER and current_user.safety_center_id:
        jurisdictions = (
            db.query(Jurisdiction)
            .filter(Jurisdiction.safety_center_id == current_user.safety_center_id, Jurisdiction.is_active == True)
            .all()
        )
    else:
        center_ids = [
            c.id for c in db.query(SafetyCenter)
            .filter(SafetyCenter.parent_station_id == current_user.station_id)
            .all()
        ]
        jurisdictions = (
            db.query(Jurisdiction)
            .filter(Jurisdiction.safety_center_id.in_(center_ids), Jurisdiction.is_active == True)
            .all()
        )

    if not jurisdictions:
        return []

    sigungu_set = {get_jurisdiction_sigungu(db, j) for j in jurisdictions}
    sigungu_set.discard(None)

    # "청주시 청원구" → "청주시"로 변환해서 기상특보 데이터 체계에 맞춤
    weather_sigungu_set = {extract_city_name(s) for s in sigungu_set}

    if not weather_sigungu_set:
        return []

    warnings = (
        db.query(WeatherWarning)
        .filter(WeatherWarning.sigungu_name.in_(weather_sigungu_set), WeatherWarning.is_active == True)
        .all()
    )

    return [
        {
            "id": w.id,
            "warn_var": w.warn_var,
            "warn_stress": w.warn_stress,
            "sigungu_name": w.sigungu_name,
            "start_time": w.start_time,
        }
        for w in warnings
    ]