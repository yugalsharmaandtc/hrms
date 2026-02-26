import os
from typing import List

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hrms"
)

# Fix Render giving postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "")

def get_allowed_origins() -> List[str]:
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    if FRONTEND_URL and FRONTEND_URL.strip():
        origins.append(FRONTEND_URL.strip())
    return origins