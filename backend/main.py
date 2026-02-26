from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_allowed_origins
from app.db.database import engine, Base
from app.models.employee import Employee      # registers Employee with Base
from app.models.attendance import Attendance  # registers Attendance with Base

# Create tables - runs on every startup, safe to run multiple times
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HRMS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import employees, attendance
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])

@app.get("/")
def root():
    return {"message": "HRMS API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy"}