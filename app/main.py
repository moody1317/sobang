import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.api.v1.auth as auth
import app.api.v1.admin as admin
import app.api.v1.station as stations

from app.core.database import Base, SessionLocal, engine
from app.api.v1.statistics import warm_ems_hourly_cache
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

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    threading.Thread(target=_warm_caches, daemon=True).start()

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
