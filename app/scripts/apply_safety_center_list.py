# app/scripts/debug_my_jurisdictions.py
from app.core.database import SessionLocal
from app.models.user import User
from app.services.jurisdiction_population_service import get_my_jurisdictions, get_jurisdiction_sigungu

if __name__ == "__main__":
    db = SessionLocal()
    user = db.query(User).filter(User.firefighter_number == "ADMIN00001").first()

    jurisdictions = get_my_jurisdictions(db, user)
    print(f"관할구역 {len(jurisdictions)}개:")
    for j in jurisdictions:
        sigungu = get_jurisdiction_sigungu(db, j)
        print(f" - id={j.id}, ward_name={j.ward_name}, safety_center_id={j.safety_center_id}, local_unit_id={j.local_unit_id} → {sigungu}")