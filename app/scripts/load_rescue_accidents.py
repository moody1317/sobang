# app/scripts/load_rescue_accidents.py
import pandas as pd
from datetime import datetime
from app.core.database import SessionLocal
from app.models.rescue_accident import RescueAccident

CSV_PATH = "app/data/소방청_구조활동현황(2024).csv"

def parse_date(value):
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def parse_time(value):
    try:
        return datetime.strptime(str(value).strip(), "%H:%M").time()
    except (ValueError, TypeError):
        return None

if __name__ == "__main__":
    db = SessionLocal()
    db.query(RescueAccident).delete()
    db.commit()

    created = 0
    chunk_no = 0

    for chunk in pd.read_csv(CSV_PATH, encoding="cp949", chunksize=50_000):
        chunk_no += 1

        for _, row in chunk.iterrows():
            db.add(RescueAccident(
                report_date=parse_date(row.get("신고년월일")),
                report_time=parse_time(row.get("신고시각")),
                dispatch_date=parse_date(row.get("출동년월일")),
                dispatch_time=parse_time(row.get("출동시각")),
                sido_nm=row.get("발생장소_시") if pd.notna(row.get("발생장소_시")) else None,
                gu_nm=row.get("발생장소_구") if pd.notna(row.get("발생장소_구")) else None,
                dong_nm=row.get("발생장소_동") if pd.notna(row.get("발생장소_동")) else None,
                accident_cause=row.get("사고원인"),
                accident_type_nm=row.get("사고원인코드명_사고종별"),
            ))
            created += 1

        db.commit()
        print(f"청크 {chunk_no} 완료 — 누적 적재 {created}건")

    print(f"전체 완료: 총 {created}건")