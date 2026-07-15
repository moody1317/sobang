# app/scripts/test_admin_dong_population.py
import json
from app.services.admin_dong_population_service import fetch_admin_dong_population_preview

if __name__ == "__main__":
    result = fetch_admin_dong_population_preview(
        admm_cd="4311300000",
        srch_fr_ym="202604",
        srch_to_ym="202605",
    )

    items = result.get("Response", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        items = [items]

    dong_names = {item.get("dongNm") for item in items}
    print("행정동명 목록:", dong_names)
    print("복대 관련:", {d for d in dong_names if d and "복대" in d})