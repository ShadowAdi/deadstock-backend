from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger import logger

async def http_exception_handler(request:Request,exc:StarletteHTTPException):
    logger.warning(f"HTTP Error: {exc.detail}")
    raise JSONResponse(
        status_code=exc.status_code,
        content={
            "success":False,
            "error":exc.detail
        }
    )
    
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": exc.errors()
        },
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Error: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error"
        },
    )