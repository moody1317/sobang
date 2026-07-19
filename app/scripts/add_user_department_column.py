from sqlalchemy import text, inspect
from app.core.database import engine
from app.models.user import Department

def add_user_department_column():
    existing_columns = {c["name"] for c in inspect(engine).get_columns("users")}
    if "department" in existing_columns:
        print("users.department 이미 존재, 건너뜀")
        return

    enum_values = ", ".join(f"'{d.value}'" for d in Department)
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE users ADD COLUMN department ENUM({enum_values}) NULL"))
    print("users.department 컬럼 추가 완료")

if __name__ == "__main__":
    add_user_department_column()
