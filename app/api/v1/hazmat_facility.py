from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.services.hazmat_facility_service import get_nearby_hazmat_facilities

router = APIRouter(prefix="/hazmat-facilities", tags=["hazmat-facilities"])

@router.get("/nearby")
def list_nearby_hazmat_facilities(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(1.0, gt=0, le=20),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    facilities = get_nearby_hazmat_facilities(db, lat, lon, radius_km)
    return [
        {
            "id": f.id,
            "entrps_nm": f.entrps_nm,
            "induty_nm": f.induty_nm,
            "rn_adres": f.rn_adres,
            "adres": f.adres,
            "latitude": float(f.latitude),
            "longitude": float(f.longitude),
        }
        for f in facilities
    ]
