# app/scripts/debug_sigungu_names.py
from app.core.database import SessionLocal
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter
from app.services.jurisdiction_population_service import get_jurisdiction_sigungu

if __name__ == "__main__":
    db = SessionLocal()
    center_ids_query = db.query(SafetyCenter).filter(
        SafetyCenter.address.like("%청원구%")
    ).all()

    for c in center_ids_query:
        j = db.query(Jurisdiction).filter(Jurisdiction.safety_center_id == c.id, Jurisdiction.is_active == True).first()
        if j:
            sigungu = get_jurisdiction_sigungu(db, j)
            print(c.station_name, "→", repr(sigungu))