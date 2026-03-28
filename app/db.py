from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
import time
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

# Retry logic with exponential backoff
def connect_with_retry(database_url: str, max_retries: int = 5, initial_delay: float = 2):
    """
    Attempt to connect to the database with exponential backoff.
    Waits for the database to be ready before attempting connection.
    """
    retry_count = 0
    delay = initial_delay
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting to connect to database (attempt {retry_count + 1}/{max_retries})...")
            engine = create_engine(database_url, echo=False, pool_pre_ping=True)
            
            # Test database connection
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            logger.info("✅ Database connection successful")
            return engine
            
        except SQLAlchemyError as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"❌ Database connection failed after {max_retries} attempts - {type(e).__name__}: {str(e)}")
                raise AppError(
                    message="Failed to connect to database",
                    status_code=500,
                    error_code="DB_CONNECTION_ERROR",
                    details={"error": str(e)}
                )
            logger.warning(f"⏳ Database not ready, retrying in {delay}s... ({type(e).__name__})")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"❌ Unexpected error during database connection - {type(e).__name__}: {str(e)}")
                raise AppError(
                    message="Unexpected error connecting to database",
                    status_code=500,
                    error_code="DB_UNEXPECTED_ERROR",
                    details={"error": str(e)}
                )
            logger.warning(f"⏳ Unexpected error, retrying in {delay}s... ({type(e).__name__})")
            time.sleep(delay)
            delay *= 2

engine = connect_with_retry(DATABASE_URL)

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