from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.services.station_service import fetch_station_data, sync_all_stations

from app.schemas.station import SafetyCenterResponse
from app.models.station import Station

from app.models.user import User, UnitType
from app.models.safety_center import SafetyCenter
from app.models.ambulance_unit import AmbulanceUnit
from app.models.aviation_unit import AviationUnit
from app.models.special_response_unit import SpecialResponseUnit
from app.models.local_unit import LocalUnit
from app.models.rescue_unit import RescueUnit

UNIT_TABLE_MAP = {
    "안전센터": SafetyCenter,
    "구급대": AmbulanceUnit,
    "항공대": AviationUnit,
    "특수대응단": SpecialResponseUnit,
    "지역대": LocalUnit,
    "119구조대": RescueUnit,
}

router = APIRouter(prefix="/stations", tags=["stations"])

@router.get("/external/test")
def test_station_api(
    page_no: int = Query(1, alias="pageNo"),
    num_of_rows: int = Query(10, alias="numOfRows"),
):
    try:
        return fetch_station_data(
            page_no=page_no,
            num_of_rows=num_of_rows,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"station api error: {e}")

@router.post("/sync")
def sync_station_data(
    num_of_rows: int = Query(100, alias="numOfRows"),
    db: Session = Depends(get_db_session),
    admin_user = Depends(require_admin),
):
    try:
        result = sync_all_stations(db, num_of_rows=num_of_rows)
        return {"message": "동기화 완료", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"sync error: {e}")
    
@router.get("/units")
def get_units_by_type(
    unit_type: str = Query(..., description="안전센터/구급대/항공대/특수대응단/지역대"),
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    model = UNIT_TABLE_MAP.get(unit_type)
    if not model:
        raise HTTPException(status_code=400, detail="유효하지 않은 소속 유형입니다.")

    items = (
        db.query(model)
        .filter(model.parent_station_id == admin_user.station_id)
        .all()
    )
    return [{"id": item.id, "name": item.station_name} for item in items]