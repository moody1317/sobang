from sqlalchemy import text
from app.core.database import engine
from app.models.user import UnitType

def add_rescue_squad_unit_type():
    enum_values = ", ".join(f"'{u.value}'" for u in UnitType)
    with engine.begin() as conn:
        conn.execute(text(
            f"ALTER TABLE users MODIFY COLUMN unit_type "
            f"ENUM({enum_values}) NOT NULL DEFAULT '{UnitType.HEADQUARTERS.value}'"
        ))
    print("users.unit_type ENUM에 119구조대 추가 완료")

if __name__ == "__main__":
    add_rescue_squad_unit_type()
