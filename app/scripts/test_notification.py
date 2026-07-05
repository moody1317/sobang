# app/scripts/test_notification.py
from datetime import datetime
from app.core.database import SessionLocal
from app.services.earthquake_service import register_earthquake_event

if __name__ == "__main__":
    db = SessionLocal()

    fake_eqk = {
        "mt": 4.5,
        "tmEqk": "20260705120000",
        "lat": 36.5,
        "lon": 127.5,
        "loc": "테스트용 가상 지진 - 충북 청주 인근",
    }

    event = register_earthquake_event(db, fake_eqk)
    print("이벤트 생성됨:", event.id if event else "실패")