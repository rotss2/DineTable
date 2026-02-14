import os

def _truthy(v: str | None) -> bool:
    return str(v or "").strip().lower() in {"1","true","yes","y","on"}

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tablequeue.db")
    # SQLAlchemy expects postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Public base URL (for QR + SMS links)
    PUBLIC_BASE_URL = (os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")

    # Admin bootstrap
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin12345")

    # Signup approval (optional)
    REQUIRE_APPROVAL = _truthy(os.getenv("REQUIRE_APPROVAL", "0"))

    # Semaphore SMS (optional)
    SEMAPHORE_API_KEY = (os.getenv("SEMAPHORE_API_KEY") or "").strip()
    SEMAPHORE_SENDER_NAME = (os.getenv("SEMAPHORE_SENDER_NAME") or "TableQueue").strip()

    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
