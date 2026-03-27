from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
from app.core.logger import logger
from app.core.errors import AppError

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    raise AppError(
        message="Database configuration is missing",
        status_code=500,
        error_code="DB_CONFIG_ERROR",
        details={"issue": "DATABASE_URL environment variable not found"}
    )

try:
    logger.info(f"Attempting to connect to database...")
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Test database connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    
    logger.info("✅ Database connection successful")
    
except SQLAlchemyError as e:
    logger.error(f"❌ Database connection failed - {type(e).__name__}: {str(e)}")
    raise AppError(
        message="Failed to connect to database",
        status_code=500,
        error_code="DB_CONNECTION_ERROR",
        details={"error": str(e)}
    )
except Exception as e:
    logger.error(f"❌ Unexpected error during database connection - {type(e).__name__}: {str(e)}")
    raise AppError(
        message="Unexpected error connecting to database",
        status_code=500,
        error_code="DB_UNEXPECTED_ERROR",
        details={"error": str(e)}
    )

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    """Database session dependency for FastAPI endpoints"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()