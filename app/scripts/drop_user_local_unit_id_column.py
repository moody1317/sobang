from sqlalchemy import text, inspect
from app.core.database import engine

def drop_local_unit_id_column():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("users")}
    if "local_unit_id" not in existing_columns:
        print("users.local_unit_id 이미 없음, 건너뜀")
        return

    with engine.begin() as conn:
        fks = inspect(engine).get_foreign_keys("users")
        fk = next((f for f in fks if f["constrained_columns"] == ["local_unit_id"]), None)
        if fk and fk.get("name"):
            conn.execute(text(f"ALTER TABLE users DROP FOREIGN KEY {fk['name']}"))
        conn.execute(text("ALTER TABLE users DROP COLUMN local_unit_id"))
    print("users.local_unit_id 컬럼 삭제 완료")

if __name__ == "__main__":
    drop_local_unit_id_column()
