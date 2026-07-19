import csv
from app.core.database import SessionLocal
from app.models.station import Station
from app.models.rescue_unit import RescueUnit

def load_rescue_units(filepath: str):
    db = SessionLocal()
    matched, unmatched = 0, 0
    unmatched_list = []

    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_name = row["station"].strip()
            address = row["address"].strip()
            rescue_name = f"{station_name} 119구조대"

            if db.query(RescueUnit).filter(RescueUnit.station_name == rescue_name).first():
                continue

            station = db.query(Station).filter(
                Station.station_name.like(f"%{station_name}%"),
                Station.unit_type == "본서",
            ).first()
            if not station:
                unmatched += 1
                unmatched_list.append((station_name, "소방서를 못 찾음"))
                continue

            db.add(RescueUnit(
                station_name=rescue_name,
                address=address,
                parent_station_id=station.id,
            ))
            matched += 1

    db.commit()
    print(f"매칭됨: {matched}, 매칭 안됨: {unmatched}")
    for name, reason in unmatched_list:
        print(f" - {name} → {reason}")

if __name__ == "__main__":
    load_rescue_units("app/data/rescue_list.csv")
