from app.core.database import SessionLocal
from app.services.jurisdiction_service import fetch_all_jurisdictions, save_jurisdictions

if __name__ == "__main__":
    db = SessionLocal()
    jurisdictions = fetch_all_jurisdictions()
    print("전체 개수:", len(jurisdictions))

    result = save_jurisdictions(db, jurisdictions)
    print(f"매칭됨: {result['matched']}, 매칭 안됨: {result['unmatched']}")
    print("매칭 안 된 이름들:")
    for name in result["unmatched_names"][:30]:   # 일단 30개만 미리보기
        print(" -", name)