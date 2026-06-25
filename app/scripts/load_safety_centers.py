import csv
from pathlib import Path
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.safety_center import SafetyCenter

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # sobang_be/ 가리킴

def load_safety_centers_from_csv(filepath: str):
    db = SessionLocal()
    matched, unmatched = 0, 0

    with open(filepath, encoding="cp949") as f:
        reader = csv.DictReader(f)
        print("실제 컬럼명:", reader.fieldnames)
        for row in reader:
            station_name = row["소방서"].strip()
            center_name = row["119안전센터명"].strip()

            station = db.query(Station).filter(
                Station.station_name.like(f"%{station_name}%")
            ).first()

            db.add(SafetyCenter(
                station_id=station.id if station else None,
                center_name=center_name,
                address=row.get("주소"),
                phone_number=row.get("전화번호"),
                fax_number=row.get("팩스번호"),
            ))

            if station:
                matched += 1
            else:
                unmatched += 1

    db.commit()
    print(f"매칭됨: {matched}, 매칭 안됨: {unmatched}")


if __name__ == "__main__":
    csv_path = BASE_DIR / "119_safety_center.csv"
    load_safety_centers_from_csv(str(csv_path))