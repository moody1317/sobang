from sqlalchemy import text, inspect
from app.core.database import engine

def add_unit_columns():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("incident_vehicle_assignments")}
    with engine.begin() as conn:
        if "safety_center_id" not in existing_columns:
            conn.execute(text("ALTER TABLE incident_vehicle_assignments ADD COLUMN safety_center_id INT NULL"))
            print("incident_vehicle_assignments.safety_center_id 컬럼 추가 완료")
        else:
            print("incident_vehicle_assignments.safety_center_id 이미 존재, 건너뜀")

        if "rescue_unit_id" not in existing_columns:
            conn.execute(text("ALTER TABLE incident_vehicle_assignments ADD COLUMN rescue_unit_id INT NULL"))
            print("incident_vehicle_assignments.rescue_unit_id 컬럼 추가 완료")
        else:
            print("incident_vehicle_assignments.rescue_unit_id 이미 존재, 건너뜀")

if __name__ == "__main__":
    add_unit_columns()
