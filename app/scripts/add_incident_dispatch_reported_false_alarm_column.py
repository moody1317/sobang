from sqlalchemy import text, inspect
from app.core.database import engine

def add_reported_false_alarm_column():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("incident_dispatches")}
    if "reported_false_alarm" in existing_columns:
        print("incident_dispatches.reported_false_alarm 이미 존재, 건너뜀")
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE incident_dispatches ADD COLUMN reported_false_alarm BOOLEAN NULL"))
    print("incident_dispatches.reported_false_alarm 컬럼 추가 완료")

if __name__ == "__main__":
    add_reported_false_alarm_column()
