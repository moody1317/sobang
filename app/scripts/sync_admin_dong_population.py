from app.core.database import SessionLocal
from app.services.admin_dong_population_service import sync_admin_dong_population

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_admin_dong_population(db, srch_fr_ym="202604", srch_to_ym="202605")
    print("처리 완료:", result["processed"])
    print("실패:", len(result["failed"]))
    for f in result["failed"][:10]:
        print(" -", f["sigungu"], f["error"])