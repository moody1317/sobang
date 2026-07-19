from sqlalchemy import text, inspect
from app.core.database import engine

def add_incident_dispatch_columns():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("incidents")}
    with engine.begin() as conn:
        for column in ("fire_truck_count", "ambulance_count"):
            if column in existing_columns:
                print(f"incidents.{column} 이미 존재, 건너뜀")
                continue
            conn.execute(text(f"ALTER TABLE incidents ADD COLUMN {column} INT NOT NULL DEFAULT 0"))
            print(f"incidents.{column} 컬럼 추가 완료")

if __name__ == "__main__":
    add_incident_dispatch_columns()
