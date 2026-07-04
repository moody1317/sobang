from app.core.database import SessionLocal
from app.services.fire_target_service import sync_fire_targets

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_fire_targets(db)
    print("생성:", result["created"])
    print("갱신:", result["updated"])