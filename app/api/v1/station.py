from fastapi import APIRouter, HTTPException, Query

from app.services.station_service import fetch_station_data

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
