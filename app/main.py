from fastapi import FastAPI

from app.api.v1 import admin, auth
from app.core.database import Base, engine
from app.models import station, user

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