from sqlalchemy.orm import Session
from backend.db.database import SessionLocal


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
