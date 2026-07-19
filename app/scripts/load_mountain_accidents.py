import pandas as pd
from datetime import datetime
from app.core.database import SessionLocal
from app.models.mountain_accident import MountainAccident

CSV_PATH = "app/data/소방청_전국 산악사고 현황_20241231.csv"

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
    df = pd.read_csv(CSV_PATH, encoding="cp949")
    db = SessionLocal()

    db.query(MountainAccident).delete()
    
    created = 0
    for _, row in df.iterrows():
        db.add(MountainAccident(
            report_date=parse_date(row.get("신고년월일")),
            report_time=parse_time(row.get("신고시각")),
            sido_nm=row.get("발생장소_시") if pd.notna(row.get("발생장소_시")) else None,
            gu_nm=row.get("발생장소_구") if pd.notna(row.get("발생장소_구")) else None,
            dong_nm=row.get("발생장소_동") if pd.notna(row.get("발생장소_동")) else None,
            ri_nm=row.get("발생장소_리") if pd.notna(row.get("발생장소_리")) else None,
            accident_cause=row.get("사고원인"),
            accident_type_nm=row.get("사고원인코드명_사고종별"),
            result_cd=row.get("처리결과코드"),
            rescued_count=int(row.get("구조인원")) if pd.notna(row.get("구조인원")) else 0,
        ))
        created += 1

    db.commit()
    print(f"적재 완료: {created}건")