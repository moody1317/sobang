# app/scripts/mark_inactive_jurisdictions.py
from app.core.database import SessionLocal
from app.models.jurisdiction import Jurisdiction

if __name__ == "__main__":
    db = SessionLocal()
    unmatched = (
        db.query(Jurisdiction)
        .filter(Jurisdiction.station_id.is_(None), Jurisdiction.safety_center_id.is_(None))
        .all()
    )
    for j in unmatched:
        j.is_active = False
    db.commit()
    print(f"{len(unmatched)}건 비활성 처리 완료")
    for j in unmatched:
        print(" -", j.ward_name)