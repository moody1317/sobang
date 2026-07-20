from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_admin, require_station_scope
from app.models.user import User
from app.models.work_schedule import WorkSchedule, ShiftType
from app.models.notification import NotificationLevel
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse, UserListResponse, UserUnitUpdateRequest
from app.schemas.work_schedule import BulkEducationRequest
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.leave import UserLeaveCreate, UserLeaveEndRequest
from app.services.auth_service import UNIT_TABLE_MAP, create_user, reset_user_password, get_users_by_station, delete_user, get_user_by_firefighter_number, update_user_unit
from app.services.notification_service import create_notification
from app.services import vehicle_service, leave_service
from app.models.station import Station

router = APIRouter(prefix="/admin", tags=["admin"])

def _resolve_unit_name(db: Session, user: User) -> str | None:
    model = UNIT_TABLE_MAP.get(user.unit_type)
    if model is not None and user.safety_center_id is not None:
        unit = db.query(model).filter(model.id == user.safety_center_id).first()
        return unit.station_name if unit else None
    return user.unit_type.value

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
        unit_name = _resolve_unit_name(db, u)

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

    unit_name = _resolve_unit_name(db, updated_user)

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

@router.get("/vehicles")
def list_vehicles(
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    return vehicle_service.get_vehicles_for_station(db, admin_user.station_id)

@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
def create_new_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        vehicle = vehicle_service.create_vehicle(db, admin_user.station_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": vehicle.id, "vehicle_type": vehicle.vehicle_type.value, "count": vehicle.count}

@router.patch("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        vehicle = vehicle_service.update_vehicle_count(db, admin_user.station_id, vehicle_id, data.count)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": vehicle.id, "vehicle_type": vehicle.vehicle_type.value, "count": vehicle.count}

@router.delete("/vehicles/{vehicle_id}")
def delete_existing_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    try:
        vehicle_service.delete_vehicle(db, admin_user.station_id, vehicle_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "차량이 삭제되었습니다."}

def _get_target_user_or_404(db: Session, admin_user: User, user_id: int) -> User:
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 사용자입니다.")
    require_station_scope(admin_user, target_user.station_id)
    return target_user

def _leave_to_dict(leave) -> dict:
    return {
        "id": leave.id,
        "leave_type": leave.leave_type.value,
        "start_date": leave.start_date.isoformat(),
        "expected_end_date": leave.expected_end_date.isoformat() if leave.expected_end_date else None,
        "end_date": leave.end_date.isoformat() if leave.end_date else None,
        "reason": leave.reason,
    }

@router.get("/users/{user_id}/leave")
def list_user_leaves(
    user_id: int,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    _get_target_user_or_404(db, admin_user, user_id)
    leaves = leave_service.get_leaves_for_user(db, user_id)
    return [_leave_to_dict(l) for l in leaves]

@router.post("/users/{user_id}/leave", status_code=status.HTTP_201_CREATED)
def start_user_leave(
    user_id: int,
    data: UserLeaveCreate,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    target_user = _get_target_user_or_404(db, admin_user, user_id)
    try:
        leave = leave_service.start_leave(db, target_user, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _leave_to_dict(leave)

@router.patch("/users/{user_id}/leave/return")
def end_user_leave(
    user_id: int,
    data: UserLeaveEndRequest,
    db: Session = Depends(get_db_session),
    admin_user: User = Depends(require_admin),
):
    target_user = _get_target_user_or_404(db, admin_user, user_id)
    try:
        leave = leave_service.end_leave(db, target_user, data.end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _leave_to_dict(leave)