from app.core.database import SessionLocal
from app.services.forest_fire_risk_service import sync_forest_fire_risk, allocate_forest_fire_risk_to_jurisdictions

if __name__ == "__main__":
    db = SessionLocal()
    result1 = sync_forest_fire_risk(db)
    print("동기화:", result1)

    result2 = allocate_forest_fire_risk_to_jurisdictions(db)
    print("배분 완료:", result2["allocated"])
    print("못 찾음:", len(result2["not_found"]))