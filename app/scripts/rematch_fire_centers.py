from app.core.database import SessionLocal
from app.models.fire_incident import FireIncident
from app.models.safety_center import SafetyCenter
from app.services.jurisdiction_service import normalize_name

if __name__ == "__main__":
    db = SessionLocal()

    centers = db.query(SafetyCenter).all()
    center_map = {normalize_name(c.station_name): c.id for c in centers}

    unmatched = db.query(FireIncident).filter(FireIncident.safety_center_id.is_(None)).all()
    matched = 0
    still_unmatched = set()

    for f in unmatched:
        center_id = center_map.get(normalize_name(f.cntr_nm or ""))
        if center_id:
            f.safety_center_id = center_id
            matched += 1
        else:
            still_unmatched.add(f.cntr_nm)

    db.commit()
    print("추가 매칭:", matched)
    print("여전히 안 됨:", len(still_unmatched))
    for name in sorted(still_unmatched):
        print(" -", name)