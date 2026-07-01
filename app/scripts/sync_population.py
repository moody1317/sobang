# app/scripts/sync_population.py
from app.core.database import SessionLocal
from app.services.population_service import sync_all_population

if __name__ == "__main__":
    db = SessionLocal()
    result = sync_all_population(db, srch_fr_ym="202604", srch_to_ym="202605")
    print("생성:", result["created"])
    print("업데이트:", result["updated"])
    if result["failed"]:
        print("실패한 시군구:")
        for f in result["failed"]:
            print(" -", f["sigungu"], f["error"])