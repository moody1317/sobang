from app.core.database import SessionLocal
from app.services.hazmat_facility_service import sync_hazmat_facilities

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_hazmat_facilities(db)
    print("전체:", result["total"], "건")
    print("신규:", result["created"], "건")
    print("갱신:", result["updated"], "건")
