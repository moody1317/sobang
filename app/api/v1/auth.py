from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user, get_db_session
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest
from app.schemas.user import UserResponse
from app.models.station import Station
from app.services.auth_service import authenticate_user, create_user_token, change_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db_session),
):
    try:
        user = authenticate_user(
            db=db,
            firefighter_number=login_data.firefighter_number,
            password=login_data.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="대원번호 또는 비밀번호가 올바르지 않습니다.",
        )
    
    access_token = create_user_token(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        must_change_password=user.must_change_password,
    )

@router.post("/change-password")
def change_my_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    try:
        change_password(db, current_user, data.current_password, data.new_password)
        return {"message": "비밀번호가 변경되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
def read_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
    ):
    station = db.query(Station).filter(Station.id == current_user.station_id).first()
    user_dict = UserResponse.model_validate(current_user).model_dump()
    user_dict["station_name"] = station.station_name if station else None
    return UserResponse(**user_dict)