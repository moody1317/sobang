from app.core.database import SessionLocal
from app.services.inspection_service import check_inspection_deadlines

if __name__ == "__main__":
    db = SessionLocal()
    result = check_inspection_deadlines(db)
    print("점검 예정 확인:", result["checked_scheduled"], "건")
    print("재점검 확인:", result["checked_recheck"], "건")
    print("알림 생성:", result["created"], "건")
