from fastapi import FastAPI
from .db import Base, engine
from .core.expectations import (
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from .core.errors import AppError
from .core.logger import logger
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="DeadStock API", version="1.0.0")

# Register exception handlers in order of specificity
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Initialize database tables
try:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database tables: {type(e).__name__}: {str(e)}")
    raise

logger.info("🚀 Application started successfully")

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker is working 🚀"}

@app.get("/health")
def health_check():
    """Health check endpoint to verify API is running"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "service": "DeadStock API",
        "version": "1.0.0"
    }