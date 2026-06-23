from fastapi import FastAPI

import app.api.v1.auth as auth
import app.api.v1.admin as admin
import app.api.v1.station as stations

from app.core.database import Base, engine
import app.models.station
import app.models.user

app = FastAPI(
    title="Sobang Backend",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Sobang Backend is running"}

app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(stations.router, prefix="/api/v1")