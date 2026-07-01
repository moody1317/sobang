# app/scripts/rematch_jurisdictions.py
from app.core.database import SessionLocal
from app.services.jurisdiction_service import rematch_unmatched_jurisdictions

if __name__ == "__main__":
    db = SessionLocal()
    result = rematch_unmatched_jurisdictions(db)
    print("추가 매칭됨:", result["matched"])
    print("여전히 안 된 것:")
    for name in result["still_unmatched"]:
        print(" -", name)