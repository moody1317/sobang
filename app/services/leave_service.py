from datetime import date
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_leave import UserLeave
from app.schemas.leave import UserLeaveCreate

def get_leaves_for_user(db: Session, user_id: int) -> list[UserLeave]:
    return (
        db.query(UserLeave)
        .filter(UserLeave.user_id == user_id)
        .order_by(UserLeave.start_date.desc())
        .all()
    )

def start_leave(db: Session, user: User, data: UserLeaveCreate) -> UserLeave:
    existing = db.query(UserLeave).filter(UserLeave.user_id == user.id, UserLeave.end_date.is_(None)).first()
    if existing:
        raise ValueError("이미 휴직 중입니다.")

    leave = UserLeave(
        user_id=user.id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        expected_end_date=data.expected_end_date,
        reason=data.reason,
    )
    db.add(leave)
    user.is_active = False
    db.commit()
    db.refresh(leave)
    return leave

def end_leave(db: Session, user: User, end_date: date | None) -> UserLeave:
    leave = db.query(UserLeave).filter(UserLeave.user_id == user.id, UserLeave.end_date.is_(None)).first()
    if not leave:
        raise ValueError("진행 중인 휴직 기록이 없습니다.")

    leave.end_date = end_date or date.today()
    user.is_active = True
    db.commit()
    db.refresh(leave)
    return leave
