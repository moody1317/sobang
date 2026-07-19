from app.core.database import SessionLocal
from app.services.fire_incident_service import sync_fire_incidents

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_fire_incidents(db, start_ymd="20250101", end_ymd="20260630")
    print("수집:", result["collected"])
    print("범위 밖 스킵:", result["skipped_out_of_range"])
    print("마지막 페이지:", result["last_page"])