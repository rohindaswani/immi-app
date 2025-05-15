from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# PostgreSQL database connection
engine = None
SessionLocal = None
Base = declarative_base()

# This will be initialized when the database URL is available
if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get a database session.
    """
    if not SessionLocal:
        raise Exception("Database connection not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()