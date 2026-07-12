from app.core.database import SessionLocal
from app.services.weather_warning_service import sync_weather_warnings

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_weather_warnings(db)
    print("저장된 특보:", result["created"])
    print("신규 발효(알림 생성):", result["newly_issued"])