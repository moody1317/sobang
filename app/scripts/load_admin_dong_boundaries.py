from app.core.database import SessionLocal
from app.services.admin_dong_boundary_service import load_admin_dong_boundary_master, attach_dong_geometry

XLSX_PATH = "app/data/KIKcd_H.20260701.xlsx"
GEOJSON_PATH = "app/data/HangJeongDong_ver20260401.geojson"

if __name__ == "__main__":
    db = SessionLocal()

    master_result = load_admin_dong_boundary_master(db, XLSX_PATH)
    print(f"행정동 마스터 적재 — 생성: {master_result['created']}, 갱신: {master_result['updated']}, 제외(폐지): {master_result['skipped']}")

    geo_result = attach_dong_geometry(db, GEOJSON_PATH)
    print(f"경계 매칭 — 매칭: {geo_result['matched']}, 미매칭: {geo_result['unmatched_count']}")
    if geo_result["unmatched_codes"]:
        print("미매칭 코드 예시:", geo_result["unmatched_codes"])
