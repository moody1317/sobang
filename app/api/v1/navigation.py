from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.navigation_service import fetch_route

router = APIRouter(prefix="/navigation", tags=["navigation"])

@router.get("/route")
def get_route(
    origin_lat: float = Query(...),
    origin_lng: float = Query(...),
    dest_lat: float = Query(...),
    dest_lng: float = Query(...),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return fetch_route(origin_lat, origin_lng, dest_lat, dest_lng)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"route api error: {e}")