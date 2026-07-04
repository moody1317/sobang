# app/scripts/check_cheongju.py
from app.services.forest_fire_risk_service import fetch_forest_fire_risk_raw, parse_forest_fire_risk

if __name__ == "__main__":
    raw = fetch_forest_fire_risk_raw(num_of_rows=300)
    items = parse_forest_fire_risk(raw)

    for item in items:
        if "청주" in item.get("sigun", "") or "청주" in item.get("doname", ""):
            print(item)