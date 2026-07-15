# app/scripts/insert_missing_units.py
import pandas as pd
from app.core.database import SessionLocal
from app.models.safety_center import SafetyCenter
from app.models.local_unit import LocalUnit

MISSING_CSV_PATH = "app/data/missing_units.csv"

if __name__ == "__main__":
    db = SessionLocal()
    df = pd.read_csv(MISSING_CSV_PATH, encoding="utf-8-sig")

    center_seq, unit_seq = 0, 0
    center_added, unit_added = 0, 0

    for _, row in df.iterrows():
        name = str(row["safety_center"]).strip()
        address = str(row["address"]).strip()
        is_local = bool(row["is_local_unit"])

        if is_local:
            unit_seq += 1
            code = f"MANUAL-LOCAL-{unit_seq:04d}"
            db.add(LocalUnit(station_code=code, station_name=name, address=address))
            unit_added += 1
        else:
            center_seq += 1
            code = f"MANUAL-SC-{center_seq:04d}"
            db.add(SafetyCenter(station_code=code, station_name=name, address=address))
            center_added += 1

    db.commit()
    print(f"안전센터 신규 추가: {center_added}건")
    print(f"지역대 신규 추가: {unit_added}건")