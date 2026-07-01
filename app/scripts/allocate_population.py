from app.core.database import SessionLocal
from app.services.jurisdiction_population_service import allocate_population_to_jurisdictions

if __name__ == "__main__":
    db = SessionLocal()
    result = allocate_population_to_jurisdictions(db, std_ym="202604")
    print("배분 완료:", result["allocated"])
    print("시군구 매칭 안 됨:", result["no_sigungu_matched"])
    print("인구데이터 없는 시군구:", result["empty_population_sigungu"])