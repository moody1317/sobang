from app.core.database import SessionLocal
from app.services.emergency_info_service import sync_ems_hourly_stats
from datetime import datetime, timedelta

if __name__ == "__main__":
    db = SessionLocal()
    months = [(datetime.now() - timedelta(days=30 * i)).strftime("%Y%m") for i in range(12)]
    result = sync_ems_hourly_stats(
        db,
        station_name="청주동부소방서",
        sido_name="충북소방본부",
        short_name="동부소방서",
        months=months,
    )
    print(result)