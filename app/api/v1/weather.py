# app/api/v1/weather.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.weather_warning import WeatherWarning
from app.services.jurisdiction_population_service import get_my_sigungu_set, extract_city_name

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/warnings")
def get_my_weather_warnings(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    sigungu_set = get_my_sigungu_set(db, current_user)
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