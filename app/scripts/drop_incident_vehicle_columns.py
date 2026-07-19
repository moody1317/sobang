from sqlalchemy import text, inspect
from app.core.database import engine

def drop_incident_vehicle_columns():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("incidents")}
    with engine.begin() as conn:
        for column in ("fire_truck_count", "ambulance_count"):
            if column not in existing_columns:
                print(f"incidents.{column} 이미 없음, 건너뜀")
                continue
            conn.execute(text(f"ALTER TABLE incidents DROP COLUMN {column}"))
            print(f"incidents.{column} 컬럼 삭제 완료")

if __name__ == "__main__":
    drop_incident_vehicle_columns()
