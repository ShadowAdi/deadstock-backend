from dotenv import load_dotenv
load_dotenv()
import os

# Load environment variables from .env file

from fastapi import FastAPI
from app.core.cors import setup_cors
from app.routes import user, listing, order, analytics
from .db import Base, engine
from app.core.errors import AppError, app_error_handler
from starlette.exceptions import HTTPException as StarletteHTTPException


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Deadstock API",
    description="API for managing sneaker reselling marketplace",
    version="1.0.0",
)

# Setup CORS
setup_cors(app)

# Add Routers
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(listing.router, prefix="/listings", tags=["listings"])
app.include_router(order.router, prefix="/orders", tags=["orders"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


# Exception handlers
@app.exception_handler(AppError)
async def custom_app_error_handler(request, exc):
    return app_error_handler(exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return app_error_handler(
        AppError(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_EXCEPTION",
        )
    )


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Deadstock API"}