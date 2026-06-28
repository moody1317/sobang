import csv
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.safety_center import SafetyCenter

def fix_safety_center_parents(filepath: str):
    db = SessionLocal()
    matched, unmatched = 0, 0
    unmatched_list = []   # ① 이 줄

    with open(filepath, encoding="cp949") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_name = row["소방서"].strip()
            center_name = row["119안전센터명"].strip()

            center = db.query(SafetyCenter).filter(
                SafetyCenter.station_name.like(f"%{center_name}%")
            ).first()
            if not center:
                unmatched += 1
                unmatched_list.append((center_name, station_name, "안전센터 자체를 못 찾음"))   # ② 이 줄
                continue

            station = db.query(Station).filter(
                Station.station_name.like(f"%{station_name}%"),
                Station.unit_type == "본서",
            ).first()
            if not station:
                unmatched += 1
                unmatched_list.append((center_name, station_name, "소방서를 못 찾음"))   # ③ 이 줄
                continue

            center.parent_station_id = station.id
            matched += 1

    db.commit()
    print(f"매칭됨: {matched}, 매칭 안됨: {unmatched}")
    print("매칭 안 된 목록:")
    for center_name, station_name, reason in unmatched_list:   # ④ 이 줄
        print(f" - {center_name} (소속: {station_name}) → {reason}")
if __name__ == "__main__":
    fix_safety_center_parents("119_safety_center.csv")