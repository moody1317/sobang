# app/scripts/sync_ems_hourly.py
from app.core.database import SessionLocal
from app.services.emergency_info_service import sync_ems_hourly_stats
from datetime import datetime, timedelta

if __name__ == "__main__":
    db = SessionLocal()
    months = [(datetime.now() - timedelta(days=30 * i)).strftime("%Y%m") for i in range(12)]
    result = sync_ems_hourly_stats(
        db,
        station_name="청주동부소방서",   # 우리 DB 기준 정식 이름
        sido_name="충북소방본부",         # 검증된 값
        short_name="동부소방서",          # 검증된 값
        months=months,
    )
    print(result)