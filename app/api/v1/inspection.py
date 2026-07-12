from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db_session, get_current_active_user
from app.models.inspection import Inspection, InspectionStatus
from app.models.user import User
from app.models.jurisdiction import Jurisdiction
from app.models.work_schedule import WorkSchedule, ShiftType
from app.schemas.inspection import InspectionCreate, InspectionCompleteRequest, InspectionResponse

router = APIRouter(prefix="/inspections", tags=["inspections"])

def _mark_patrol_day(db: Session, user_id: int, target_date) -> None:
    """점검 완료 시, 담당 대원의 근무일정에 순찰 배지를 자동으로 켠다."""
    schedule = db.query(WorkSchedule).filter(
        WorkSchedule.user_id == user_id, WorkSchedule.date == target_date
    ).first()

    if schedule:
        schedule.is_patrol = True
    else:
        db.add(WorkSchedule(
            user_id=user_id,
            date=target_date,
            shift_type=ShiftType.주간,   # 근무 기록이 아예 없던 날이면 기본값(주간)으로 생성
            is_patrol=True,
            is_education=False,
        ))

def _to_response(db: Session, inspection: Inspection) -> InspectionResponse:
    jurisdiction = db.query(Jurisdiction).filter(Jurisdiction.id == inspection.jurisdiction_id).first()
    inspector = db.query(User).filter(User.id == inspection.inspector_id).first()
    data = InspectionResponse.model_validate(inspection).model_dump()
    data["ward_name"] = jurisdiction.ward_name if jurisdiction else None
    data["inspector_name"] = inspector.name if inspector else None
    return InspectionResponse(**data)

@router.post("", response_model=InspectionResponse, status_code=201)
def create_inspection(
    data: InspectionCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    jurisdiction = db.query(Jurisdiction).filter(Jurisdiction.id == data.jurisdiction_id).first()
    if not jurisdiction:
        raise HTTPException(status_code=404, detail="관할구역을 찾을 수 없습니다.")

    inspection = Inspection(
        jurisdiction_id=data.jurisdiction_id,
        target=data.target,
        inspection_type=data.inspection_type,
        status=InspectionStatus.예정,
        scheduled_date=data.scheduled_date,
        inspector_id=current_user.id,   # 클라이언트가 보낸 이름이 아니라 토큰의 실제 유저로 저장
        note=data.note,
    )
    db.add(inspection)

    db.commit()
    db.refresh(inspection)
    return _to_response(db, inspection)

@router.get("", response_model=list[InspectionResponse])
def list_inspections(
    status: InspectionStatus = None,
    db: Session = Depends(get_db_session),
):
    query = db.query(Inspection)
    if status:
        query = query.filter(Inspection.status == status)
    items = query.order_by(desc(Inspection.scheduled_date)).all()
    return [_to_response(db, i) for i in items]

@router.patch("/{inspection_id}/start", response_model=InspectionResponse)
def start_inspection(inspection_id: int, db: Session = Depends(get_db_session)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="점검 기록을 찾을 수 없습니다.")
    inspection.status = InspectionStatus.진행
    db.commit()
    db.refresh(inspection)
    return _to_response(db, inspection)

@router.patch("/{inspection_id}/complete", response_model=InspectionResponse)
def complete_inspection(inspection_id: int, data: InspectionCompleteRequest, db: Session = Depends(get_db_session)):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="점검 기록을 찾을 수 없습니다.")

    inspection.status = InspectionStatus.완료
    inspection.result = data.result
    inspection.result_detail = data.result_detail
    inspection.next_inspection_date = data.next_inspection_date
    inspection.completed_at = datetime.now()

    _mark_patrol_day(db, inspection.inspector_id, inspection.completed_at.date())

    db.commit()
    db.refresh(inspection)
    return _to_response(db, inspection)