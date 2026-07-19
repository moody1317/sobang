from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin, require_station_scope
from app.models.user import User, UnitType
from app.models.safety_center import SafetyCenter
from app.models.work_schedule import WorkSchedule, ShiftType
from app.models.notification import NotificationLevel
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse, UserListResponse, UserUnitUpdateRequest
from app.schemas.work_schedule import BulkEducationRequest
from app.services.auth_service import create_user, reset_user_password, get_users_by_station, delete_user, get_user_by_firefighter_number, update_user_unit
from app.services.notification_service import create_notification
from app.models.station import Station

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    require_station_scope(admin_user, user_data.station_id)

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
    target_user = get_user_by_firefighter_number(db, firefighter_number)
    if not target_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 대원번호입니다.")
    require_station_scope(admin_user, target_user.station_id)

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
            unit_name = center.station_name if center else None
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

    target_user = get_user_by_firefighter_number(db, firefighter_number)
    if not target_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 대원번호입니다.")
    require_station_scope(admin_user, target_user.station_id)

    try:
        name = delete_user(db, firefighter_number)
        return {"message": f"{name}님의 계정이 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUnitUpdateRequest,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        updated_user = update_user_unit(db, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    station = db.query(Station).filter(Station.id == updated_user.station_id).first()
    station_name = station.station_name if station else None

    if updated_user.unit_type == UnitType.SAFETY_CENTER:
        center = db.query(SafetyCenter).filter(SafetyCenter.id == updated_user.safety_center_id).first()
        unit_name = center.station_name if center else None   
    else:
        unit_name = updated_user.unit_type.value

    user_dict = UserResponse.model_validate(updated_user).model_dump()
    user_dict["station_name"] = station_name
    user_dict["unit_name"] = unit_name
    return UserResponse(**user_dict)

@router.post("/schedules/bulk-education")
def bulk_register_education(
    data: BulkEducationRequest,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    users = get_users_by_station(db, admin_user.station_id)

    for u in users:
        schedule = db.query(WorkSchedule).filter(
            WorkSchedule.user_id == u.id, WorkSchedule.date == data.date
        ).first()
        if schedule:
            schedule.is_education = True
            schedule.title = data.title
        else:
            db.add(WorkSchedule(
                user_id=u.id,
                date=data.date,
                shift_type=ShiftType.주간,
                is_patrol=False,
                is_education=True,
                title=data.title,
            ))

    create_notification(
        db,
        level=NotificationLevel.SAFE,
        source="schedule",
        title="교육 일정 등록",
        message=f"{data.date.isoformat()} '{data.title}' 교육이 전체 대원 일정에 추가되었습니다.",
        station_id=admin_user.station_id,
    )

    db.commit()
    return {"count": len(users)}