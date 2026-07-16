from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.work_schedule import WorkSchedule
from app.schemas.work_schedule import WorkScheduleUpsert, WorkScheduleResponse

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("/my", response_model=list[WorkScheduleResponse])
def get_my_schedule(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    items = db.query(WorkSchedule).filter(
        WorkSchedule.user_id == current_user.id,
        extract("year", WorkSchedule.date) == year,
        extract("month", WorkSchedule.date) == month,
    ).all()
    return items


@router.put("/my/{schedule_date}", response_model=WorkScheduleResponse)
def upsert_my_schedule(
    schedule_date: date,
    data: WorkScheduleUpsert,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    existing = db.query(WorkSchedule).filter(
        WorkSchedule.user_id == current_user.id,
        WorkSchedule.date == schedule_date,
    ).first()

    if existing:
        existing.shift_type = data.shift_type
        existing.start_time = data.start_time
        existing.end_time = data.end_time
        existing.is_patrol = data.is_patrol
        existing.is_education = data.is_education
        existing.title = data.title
        schedule = existing
    else:
        schedule = WorkSchedule(
            user_id=current_user.id,
            date=schedule_date,
            shift_type=data.shift_type,
            start_time=data.start_time,
            end_time=data.end_time,
            is_patrol=data.is_patrol,
            is_education=data.is_education,
            title=data.title,
        )
        db.add(schedule)

    db.commit()
    db.refresh(schedule)
    return schedule