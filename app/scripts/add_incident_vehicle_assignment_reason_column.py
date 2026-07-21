from sqlalchemy import text, inspect
from app.core.database import engine

def add_reason_column():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("incident_vehicle_assignments")}
    if "reason" in existing_columns:
        print("incident_vehicle_assignments.reason 이미 존재, 건너뜀")
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE incident_vehicle_assignments ADD COLUMN reason VARCHAR(200) NULL"))
    print("incident_vehicle_assignments.reason 컬럼 추가 완료")

if __name__ == "__main__":
    add_reason_column()
