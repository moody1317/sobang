# app/scripts/debug_yulryang.py
from app.core.database import SessionLocal
from app.models.jurisdiction import Jurisdiction
from app.models.safety_center import SafetyCenter
from app.models.station import Station
from app.services.jurisdiction_service import normalize_name

if __name__ == "__main__":
    db = SessionLocal()

    print("--- jurisdictions.ward_name ---")
    for j in db.query(Jurisdiction).filter(Jurisdiction.ward_name.like("%율량%")).all():
        print("raw:", repr(j.ward_name))
        print("normalized:", repr(normalize_name(j.ward_name)))

    print("--- safety_centers_v2.station_name ---")
    for c in db.query(SafetyCenter).filter(SafetyCenter.station_name.like("%율량%")).all():
        print("raw:", repr(c.station_name))
        print("normalized:", repr(normalize_name(c.station_name)))

    print("--- stations.station_name ---")
    for s in db.query(Station).filter(Station.station_name.like("%율량%")).all():
        print("raw:", repr(s.station_name))
        print("normalized:", repr(normalize_name(s.station_name)))