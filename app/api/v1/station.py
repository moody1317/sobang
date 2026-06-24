from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.services.station_service import fetch_station_data, sync_all_stations

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