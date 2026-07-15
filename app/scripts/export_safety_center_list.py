# app/scripts/export_safety_center_list.py
import csv
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.safety_center import SafetyCenter

if __name__ == "__main__":
    db = SessionLocal()

    stations = db.query(Station).order_by(Station.station_name).all()

    rows = []
    for station in stations:
        centers = (
            db.query(SafetyCenter)
            .filter(SafetyCenter.parent_station_id == station.id)
            .order_by(SafetyCenter.station_name)
            .all()
        )
        if not centers:
            rows.append([station.station_name, "(산하 안전센터 없음)", "", ""])
            continue
        for center in centers:
            rows.append([station.station_name, center.station_name, center.address or "", ""])

    output_path = "safety_center_list.csv"
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["소방서명", "안전센터명", "주소", "관할동(크롤링 결과 기입란)"])
        writer.writerows(rows)

    print(f"저장 완료: {output_path} (총 {len(rows)}행)")