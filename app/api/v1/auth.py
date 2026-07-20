from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_user, get_db_session
from app.core.config import settings
from app.models.user import User, UnitType
from app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest, PasswordVerifyRequest
from app.schemas.user import UserResponse, ProfileUpdateRequest
from app.models.station import Station
from app.services.auth_service import authenticate_user, create_user_token, change_password, update_profile
from app.core.security import verify_password
from app.models.safety_center import SafetyCenter
from app.models.ambulance_unit import AmbulanceUnit
from app.models.aviation_unit import AviationUnit
from app.models.special_response_unit import SpecialResponseUnit
from app.models.local_unit import LocalUnit

UNIT_TABLE_MAP = {
    UnitType.SAFETY_CENTER: SafetyCenter,
    UnitType.AMBULANCE: AmbulanceUnit,
    UnitType.AVIATION: AviationUnit,
    UnitType.SPECIAL_RESPONSE: SpecialResponseUnit,
    UnitType.LOCAL_UNIT: LocalUnit,
}

router = APIRouter(prefix="/auth", tags=["auth"])

def resolve_unit_name(db: Session, user: User, station_name: str) -> str:
    model = UNIT_TABLE_MAP.get(user.unit_type)
    if model is not None and user.safety_center_id:
        unit = db.query(model).filter(model.id == user.safety_center_id).first()
        return unit.station_name if unit else station_name
    return user.unit_type.value  # 본서, 기타 등

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    response: Response,
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

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        must_change_password=user.must_change_password,
    )

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"message": "로그아웃되었습니다."}

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
    station_name = station.station_name if station else None
    unit_name = resolve_unit_name(db, current_user, station_name)

    user_dict = UserResponse.model_validate(current_user).model_dump()
    user_dict["station_name"] = station_name
    user_dict["unit_name"] = unit_name
    return UserResponse(**user_dict)

@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    try:
        updated_user = update_profile(db, current_user, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    station = db.query(Station).filter(Station.id == updated_user.station_id).first()
    station_name = station.station_name if station else None

    if updated_user.unit_type == UnitType.SAFETY_CENTER:
        safety_center = db.query(SafetyCenter).filter(
            SafetyCenter.id == updated_user.safety_center_id
        ).first()
        unit_name = safety_center.station_name if safety_center else station_name
    else:
        unit_name = updated_user.unit_type.value

    user_dict = UserResponse.model_validate(updated_user).model_dump()
    user_dict["station_name"] = station_name
    user_dict["unit_name"] = unit_name
    return UserResponse(**user_dict)

@router.post("/verify-password")
def verify_my_password(
    data: PasswordVerifyRequest,
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")
    return {"verified": True}