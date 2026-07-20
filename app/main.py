import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.api.v1.auth as auth
import app.api.v1.admin as admin
import app.api.v1.station as stations

from app.core.database import Base, SessionLocal, engine
from app.api.v1.statistics import warm_ems_hourly_cache
from app.services.earthquake_service import poll_recent_earthquakes
from app.services.weather_warning_service import sync_weather_warnings
from app.services.inspection_service import check_inspection_deadlines
from app.services.risk_score_service import (
    calculate_jurisdiction_risk_scores, allocate_risk_score_to_dongs, snapshot_dong_risk_scores,
)
import app.models.station
import app.models.user
import app.models.safety_center

import app.api.v1.incident as incidents
import app.models.incident
import app.models.notification
import app.api.v1.navigation as navigation

from app.api.v1 import notifications

from app.api.v1 import weather
from app.api.v1 import inspection
from app.api.v1 import jurisdiction
from app.api.v1 import work_schedule
from app.api.v1 import statistics
from app.api.v1 import risk_map

app = FastAPI(
    title="Sobang Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1317"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _warm_caches():
    db = SessionLocal()
    try:
        warm_ems_hourly_cache(db)
    finally:
        db.close()

EARTHQUAKE_POLL_SECONDS = 5 * 60
WEATHER_POLL_SECONDS = 30 * 60
DAILY_SECONDS = 24 * 60 * 60

def _run_periodically(name: str, fn, interval_seconds: int):
    while True:
        db = SessionLocal()
        try:
            fn(db)
        except Exception as e:  # 한 번 실패해도 폴링 자체는 계속 돈다
            db.rollback()
            print(f"[{name}] 폴링 중 오류:", e)
        finally:
            db.close()
        time.sleep(interval_seconds)

def _recalculate_risk_scores(db):
    calculate_jurisdiction_risk_scores(db)
    allocate_risk_score_to_dongs(db)
    snapshot_dong_risk_scores(db)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    threading.Thread(target=_warm_caches, daemon=True).start()
    threading.Thread(
        target=_run_periodically, args=("지진", poll_recent_earthquakes, EARTHQUAKE_POLL_SECONDS), daemon=True
    ).start()
    threading.Thread(
        target=_run_periodically, args=("기상특보", sync_weather_warnings, WEATHER_POLL_SECONDS), daemon=True
    ).start()
    threading.Thread(
        target=_run_periodically, args=("점검기한", check_inspection_deadlines, DAILY_SECONDS), daemon=True
    ).start()
    threading.Thread(
        target=_run_periodically, args=("위험점수", _recalculate_risk_scores, DAILY_SECONDS), daemon=True
    ).start()

@app.get("/")
def root():
    return {"message": "Sobang Backend is running"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(stations.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(inspection.router, prefix="/api/v1")
app.include_router(jurisdiction.router, prefix="/api/v1")
app.include_router(work_schedule.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")
app.include_router(navigation.router, prefix="/api/v1")
app.include_router(risk_map.router, prefix="/api/v1")
