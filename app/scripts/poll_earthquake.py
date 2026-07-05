from app.core.database import SessionLocal
from app.services.earthquake_service import poll_recent_earthquakes

if __name__ == "__main__":
    db = SessionLocal()
    result = poll_recent_earthquakes(db)
    print("확인:", result["checked"])
    print("신규 등록:", result["created"])
    print("해외 지진 스킵:", result["skipped_foreign"])