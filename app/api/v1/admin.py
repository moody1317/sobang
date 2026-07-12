from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin
from app.models.user import User, UnitType
from app.models.safety_center import SafetyCenter
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse, UserListResponse
from app.services.auth_service import create_user, reset_user_password, get_users_by_station, delete_user
from app.models.station import Station

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        new_user, temp_password = create_user(db=db, user_data=user_data)
        return UserCreateResponse(
            **UserResponse.model_validate(new_user).model_dump(),
            temp_password = temp_password,
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.post("/users/{firefighter_number}/reset-password", response_model=UserCreateResponse)
def reset_password(
    firefighter_number: str,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        user, temp_password = reset_user_password(db, firefighter_number)
        return UserCreateResponse(
            **UserResponse.model_validate(user).model_dump(),
            temp_password=temp_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/users", response_model=list[UserListResponse])
def list_users(
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    users = get_users_by_station(db, admin_user.station_id)

    station = db.query(Station).filter(Station.id == admin_user.station_id).first()
    station_name = station.station_name if station else None

    result = []
    for u in users:
        if u.unit_type == UnitType.SAFETY_CENTER:
            center = db.query(SafetyCenter).filter(SafetyCenter.id == u.safety_center_id).first()
            unit_name = center.center_name if center else None
        else:
            unit_name = u.unit_type.value

        user_dict = UserListResponse.model_validate(u).model_dump()
        user_dict["station_name"] = station_name
        user_dict["unit_name"] = unit_name
        result.append(UserListResponse(**user_dict))

    return result

@router.delete("/users/{firefighter_number}")
def delete_existing_user(
    firefighter_number: str,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    if firefighter_number == admin_user.firefighter_number:
        raise HTTPException(status_code=400, detail="본인 계정은 삭제할 수 없습니다.")

    try:
        name = delete_user(db, firefighter_number)
        return {"message": f"{name}님의 계정이 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))