from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, get_current_active_user
from app.models.user import User, UnitType
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter

router = APIRouter(prefix="/jurisdictions", tags=["jurisdictions"])

@router.get("/my")
def list_my_jurisdictions(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.unit_type == UnitType.SAFETY_CENTER and current_user.safety_center_id:
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id == current_user.safety_center_id, Jurisdiction.is_active == True
        ).all()
    else:
        center_ids = [
            c.id for c in db.query(SafetyCenter)
            .filter(SafetyCenter.parent_station_id == current_user.station_id)
            .all()
        ]
        jurisdictions = db.query(Jurisdiction).filter(
            Jurisdiction.safety_center_id.in_(center_ids), Jurisdiction.is_active == True
        ).all()

    return [{"id": j.id, "ward_name": j.ward_name} for j in jurisdictions]