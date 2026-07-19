from app.core.database import SessionLocal
from app.services.ems_incident_service import sync_ems_incidents

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_ems_incidents(db, start_ymd="20250101", end_ymd="20260630")
    print("수집:", result["collected"])
    print("마지막 페이지:", result["last_page"])